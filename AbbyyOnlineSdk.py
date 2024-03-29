import shutil
import xml.dom.minidom
import requests


class ProcessingSettings:
	Language = "English"
	OutputFormat = "txt"


class Task:
	Status = "Unknown"
	Id = None
	DownloadUrl = None

	def is_active(self):
		if self.Status == "InProgress" or self.Status == "Queued":
			return True
		else:
			return False


class AbbyyOnlineSdk:
	ServerUrl = "http://cloud-eu.ocrsdk.com/"

	ApplicationId = "Enter-Your-Application-ID"
	Password = "Enter-password"
	Proxies = {}

	def process_image(self, file, settings):
		url_params = {
			"language": settings.Language,
			"exportFormat": settings.OutputFormat
		}
		request_url = self.get_request_url("processImage")

		
		response = requests.post(request_url, data=file, params=url_params,
								 auth=(self.ApplicationId, self.Password), proxies=self.Proxies)

		# Any response other than HTTP 200 means error - in this case exception will be thrown
		response.raise_for_status()

		# parse response xml and extract task ID
		task = self.decode_response(response.text)
		return task

	def get_task_status(self, task):
		if task.Id.find('00000000-0') != -1:
			# GUID_NULL is being passed. This may be caused by a logical error in the calling code
			print("Null task id passed")
			return None

		url_params = {"taskId": task.Id}
		status_url = self.get_request_url("getTaskStatus")

		response = requests.get(status_url, params=url_params,
								auth=(self.ApplicationId, self.Password), proxies=self.Proxies)
		task = self.decode_response(response.text)
		return task

	def download_result(self, task):
		get_result_url = task.DownloadUrl
		if get_result_url is None:
			print("No download URL found")
			return

		file_response = requests.get(get_result_url, stream=True, proxies=self.Proxies)
		with open('file.txt', 'wb') as output_file:
			shutil.copyfileobj(file_response.raw, output_file)

	def decode_response(self, xml_response):
		""" Decode xml response of the server. Return Task object """
		dom = xml.dom.minidom.parseString(xml_response)
		task_node = dom.getElementsByTagName("task")[0]
		task = Task()
		task.Id = task_node.getAttribute("id")
		task.Status = task_node.getAttribute("status")
		if task.Status == "Completed":
			task.DownloadUrl = task_node.getAttribute("resultUrl")
		return task

	def get_request_url(self, url):
		return self.ServerUrl.strip('/') + '/' + url.strip('/')
