import urllib.request


class InstanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        header_name = "instance_id"
        try:
            instance_id = (
                urllib.request.urlopen(
                    "http://169.254.169.254/latest/meta-data/instance-id"
                )
                .read()
                .decode()
            )
            response[header_name] = instance_id
            return response

        except:
            response[header_name] = 4
            return response