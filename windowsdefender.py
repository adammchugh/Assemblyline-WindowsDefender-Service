import json
import os
import time
import subprocess
import tempfile

from subprocess import PIPE, TimeoutExpired

from assemblyline_v4_service.common.base import ServiceBase
from assemblyline_v4_service.common.result import Result, ResultSection, BODY_FORMAT


class WindowsDefender(ServiceBase):
    def __init__(self, config=None):
        super(WindowsDefender, self).__init__(config)

    def start(self):
        self.log.info(f"start() from {self.service_attributes.name} service called")

    def execute(self, request):
        start = time.time()

        result = Result()

        file_path = request.file_path
        timeout = self.service_attributes.timeout-5

        try:
            mpclient = subprocess.run(["/opt/al_service/loadlibrary/mpclient", file_path], timeout=max(timeout+start-time.time(), 5), stdout=PIPE, stderr=PIPE, universal_newlines=True)
        except TimeoutExpired:
            mpclient.kill()
            mpclient.stdout.close()
            mpclient.stderr.close()
            mpclient = None

        if mpclient is None:            
            result.add_section(ResultSection('mpclient timed out'))
        elif mpclient.returncode != 0:
            raise RuntimeError(f'mpclient returned a non-zero exit status {mpclient.returncode}\n'
                               f'stderr:\n{mpclient.stderr}')
        else:       
            output = mpclient.stderr.strip().split("\n")
            if (len(output) == 3):
                text_section = ResultSection(output[2].split(":", 1)[1])
                text_section.set_heuristic(1)
                result.add_section(text_section)
            else:
                text_section = ResultSection("No detection")
                result.add_section(text_section)

        request.result = result        
