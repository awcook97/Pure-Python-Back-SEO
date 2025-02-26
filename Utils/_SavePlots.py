import matplotlib.pyplot as plt

def savePlt(data, labels, title, filename):
	plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
	plt.title(title)
	#plt.show()
	plt.savefig(filename)
 
if __name__ == "__main__":
	data = [60, 40]
	labels = ["60%", "40%"]
	title = "Test Pie Chart"
	filename = "test.png"
	savePlt(data, labels, title, filename)