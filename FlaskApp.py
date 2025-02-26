from flask import Flask, render_template, request, jsonify, send_file
import dearpygui.dearpygui as dpg
import threading
import os
class FlaskApp:
    def __init__(self, agency):
        self.agency = agency
        self.currentReports = list()
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', agency=self.agency)

        # @self.app.route('/generate_report', methods=['POST'])
        # def generate_report():
        #     data = request.get_json()
        #     self.agency.generateReport(data)
        #     return '', 204

        @self.app.route('/remove_report_automation', methods=['POST'])
        def remove_report_automation():
            data = request.get_json()
            self.agency.removeReportAutomation(data)
            return '', 204

        # @self.app.route('/start_reports', methods=['POST'])
        # def start_reports():
        #     self.agency.start_reports()
        #     return '', 204

        @self.app.route('/stop_reports', methods=['POST'])
        def stop_reports():
            self.agency.stop_reports()
            return '', 204

        @self.app.route('/update_checkbox', methods=['POST'])
        def update_checkbox():
            data = request.get_json()
            checkbox_id = data['checkboxId']
            is_checked = data['isChecked']
            
            if checkbox_id == 'checkTargetKeywords':
                dpg.set_value(self.agency.checkTargetKeywords, is_checked)
            elif checkbox_id == 'checkTargetLocations':
                dpg.set_value(self.agency.checkTargetLocations, is_checked)
            elif checkbox_id == 'checkTargetMaps1':
                dpg.set_value(self.agency.checkTargetMaps1, is_checked)
            elif checkbox_id == 'checkTargetMaps2':
                dpg.set_value(self.agency.checkTargetMaps2, is_checked)
            elif checkbox_id == 'checkTargetMaps5':
                dpg.set_value(self.agency.checkTargetMaps5, is_checked)
            elif checkbox_id == 'checkTargetMaps15':
                dpg.set_value(self.agency.checkTargetMaps15, is_checked)
            elif checkbox_id == 'checkTargetMaps25':
                dpg.set_value(self.agency.checkTargetMaps25, is_checked)
            elif checkbox_id == 'checkTargetMaps50':
                dpg.set_value(self.agency.checkTargetMaps50, is_checked)
            elif checkbox_id == 'checkWebsiteAudit':
                dpg.set_value(self.agency.checkWebsiteAudit, is_checked)
            
            return '', 204

        @self.app.route('/update_client', methods=['POST'])
        def update_client(*args, **kwargs):
            data = request.get_json()
            selected_client = data['selectedClient']
            
            dpg.set_value(self.agency.clientSelector,selected_client)
            self.agency.selectClient()
            reportDir = f"{self.agency.agency.output_directory}/reports/{selected_client}"
            self.currentReports.clear()
            if os.path.exists(reportDir):
                for file in os.listdir(reportDir):
                    if file.endswith('.docx'):
                        self.currentReports.append({
                            "fileName": file, 
                            "path":reportDir+file
                        })
            return '', 204


        @self.app.route('/get_reports', methods=['POST'])
        def get_reports():
            data = request.get_json()
            selected_client = data['selectedClient']
            
            report_dir = f"{self.agency.agency.output_directory}/reports/{selected_client}"
            reports = []
            
            if os.path.exists(report_dir):
                for file in os.listdir(report_dir):
                    if file.endswith('.docx'):
                        reports.append({
                            "fileName": file,
                            "path": os.path.join(report_dir, file)
                        })
            
            return jsonify({"reports": reports})

        @self.app.route('/download_report')
        def download_report():
            filename = request.args.get('filename')
            client = request.args.get('client')
            report_path = request.args.get('path')
            
            return send_file(report_path, as_attachment=True)

    
        @self.app.route('/generate_report', methods=['POST'])
        def generate_report():
            self.agency.generateReport()
            return '', 204

        @self.app.route('/start_reports', methods=['POST'])
        def start_reports():
            self.agency.start_reports()
            return '', 204

    def run(self, debug: bool=True, host: str='0.0.0.0', port: int=5000):
        threading.Thread(target=self.app.run, kwargs={"host":host, "port":port, "debug":debug}).start()