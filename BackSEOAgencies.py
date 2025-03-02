#!/usr/bin python3.12
# from core import coreUI["Core"]


from BackSEOSettings import BackSEOSettings
import dearpygui.dearpygui as dpg
import inspect
import time
import multiprocessing
from multiprocessing import Queue, pool
import threading


from BackSEODataHandler import *  # noqa: F403
from BackSEOApplicationManager import BackSEOApplicationManager




# import cython

BackDataHandler = getBackSEODataHandler()  # type: BackSEODataHandler  # noqa: F405
job_queue = BackDataHandler.getJobQ()  # type: Queue
result_queue = BackDataHandler.getRQ()  # type: Queue


def baddy(l):  # noqa: E741
    global lock
    lock = l


def runJob(job, *args):
    # print(os.getpid())
    result = job(*args)
    # print(*args)
    return result


def worker(job_queue: Queue, result_queue: Queue):
    # print("Worker started")
    while True:
        job = job_queue.get()
        # print(job)
        if job == "STOP":
            break
        # print("hi")
        callback, args = job
        res = callback(*args)
        result_queue.put(res)


def is_slow(job):
    # print(job.__name__)
    # name = job.__name__

    return job.__name__ in ["run_process_with_userdata", "search"]


def myrun_callbacks(*args, jobs, job_queue):
    if jobs is None:
        return
    dpg.save_init_file("bseodef.ini")
    for job in jobs:
        callback = job[0]
        if callback is None:
            continue
        sig = inspect.signature(job[0])
        args = []
        for arg in range(len(sig.parameters)):
            if arg + 1 < len(job):
                args.append(job[arg + 1])

        if is_slow(callback):
            job_queue.put((callback, args))
        else:
            callback(*args)


def gui_thread(job_queue: Queue, result_queue: Queue, backseosettings: BackSEOSettings):
    dpg.create_context()
    dpg.configure_app(
        manual_callback_management=True,
        init_file="bseodef.ini",
        auto_save_init_file=True,
        load_init_file="bseodef.ini",
        docking=True,
        docking_space=False,
        wait_for_input=not backseosettings.animations,
    )
    theviewport = dpg.create_viewport(
        title="Back SEO Agency",
        width=backseosettings.width,
        height=backseosettings.height,
        vsync=backseosettings.vsync,
    )
    backseosettings.setVp(theviewport)
    BackDataHandler.registry()
    BackDataHandler.setSettings(backseosettings)
    backManager = BackSEOApplicationManager()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        if BackDataHandler.updateall:
            backManager.update(
                BackDataHandler.updateMessage[0], BackDataHandler.updateMessage[1]
            )
            ##################################
            # 	FORMER BACKMANGER			##
            # 	KEEP IN CASE OF EMERGENCY	##
            ##################################
            # for key, val in coreUI.items():
            # 	val.update(BackDataHandler.updateMessage[0], BackDataHandler.updateMessage[1])
            BackDataHandler.finishedUpdates()
        if not result_queue.empty():
            result = result_queue.get()
            if result[0] == "call":
                _, cb, args = result
                cb(*args)
            elif result[0] == "core":
                # ("core", "Editor", "search", myC)
                myT = threading.Thread(
                    target=backManager.modules[result[1]].update,
                    args=(result[2], result[3]),
                )
                # myT = threading.Thread(target=coreUI[result[1]].update, args=(result[2], result[3]))
                myT.start()
            else:
                BackDataHandler.sendData(result)
        backManager.updateUDatas()
        ##################################
        # 	FORMER BACKMANGER			##
        # 	KEEP IN CASE OF EMERGENCY	##
        ##################################
        # for key, val in coreUI.items():
        # 	val.checkQueue()
        backManager.runCommands()
        jobs = dpg.get_callback_queue()
        myrun_callbacks(jobs=jobs, job_queue=job_queue)
        dpg.set_value(
            BackDataHandler.loader3, dpg.get_frame_rate() / (backseosettings.fps + 1)
        )
        dpg.set_value(BackDataHandler.strLoader1, f"FPS: {dpg.get_frame_rate()}")
        if not backseosettings.vsync and backseosettings.fps > 0:
            time.sleep(1 / backseosettings.fps)
    dpg.destroy_context()


def otherMain(backPool: pool.Pool, backseosettings: BackSEOSettings):
    BackDataHandler = getBackSEODataHandler()  # type: BackSEODataHandler  # noqa: F405
    BackDataHandler.setPool(backPool)
    BackDataHandler.setLock(lock)
    # print(BackDataHandler)
    job_queue = BackDataHandler.getJobQ()  # type: Queue
    result_queue = BackDataHandler.getRQ()  # type: Queue
    # BackDataHandler.startPool()
    # myCores = 4
    # myT = threading.Thread(target=gui_thread, args=(job_queue,result_queue,))
    # myT.start()
    helperthreads = backseosettings.helperthreads
    for _ in range(helperthreads):
        p = threading.Thread(
            target=worker,
            args=(
                job_queue,
                result_queue,
            ),
        )
        p.start()
    gui_thread(job_queue, result_queue, backseosettings)

    # with concurrent.futures.ProcessPoolExecutor(max_workers=myCores) as executor:
    # 		jobs = BackDataHandler.
    # 		run_callbacks(jobs, job_queue)
    # 		dpg.set_value(BackDataHandler.loader3, dpg.get_frame_rate()/120)
    # 		dpg.set_value(BackDataHandler.strLoader1, f"FPS: {dpg.get_frame_rate()}")
    # 		time.sleep(0.1)
    for _ in range(helperthreads):
        job_queue.put("STOP")
        # p.join()


if __name__ == "__main__":
    multiprocessing.freeze_support()

    backseosettings = BackSEOSettings()
    global lock
    lock = multiprocessing.Lock()
    with pool.Pool(
        processes=int(backseosettings.cpucores), initargs=(lock,)
    ) as backPool:
        otherMain(backPool, backseosettings)
