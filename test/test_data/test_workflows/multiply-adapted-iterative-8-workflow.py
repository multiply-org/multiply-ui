import datetime
from pmonitor import PMonitor


class MultiplyAdaptedIterative8(PMonitor):

    def __init__(self, parameters):
        PMonitor.__init__(self,
                          ['none', parameters['data_root']],
                          request=parameters['requestName'],
                          hosts=[('localhost', 10)],
                          types=[('test_script_1.py', 2), ('test_script_2.py', 2), ('test_script_3.py', 2)],
                          logdir=parameters['log_dir'],
                          simulation='simulation' in parameters and parameters['simulation'])
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))

    def create_workflow(self):
        out_1 = self._data_root + '/' + 'out_1'
        out_2 = self._data_root + '/' + 'out_2'
        out_3 = self._data_root + '/' + 'out_3'

        cursor = self._start
        while cursor <= self._stop:
            date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._step
            cursor -= self._one_day_step
            if cursor > self._stop:
                cursor = self._stop
            next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._one_day_step
            out_1_for_date = out_1 + '/' + date
            out_2_for_date = out_2 + '/' + date
            out_3_for_date = out_3 + '/' + date
            self.execute('test_script_1.py', [], [out_1_for_date],
                         parameters=[self._request_file, date, next_date])
            self.execute('test_script_2.py', [out_1_for_date], [out_2_for_date],
                         parameters=[self._request_file])
            self.execute('test_script_3.py', [out_2_for_date], [out_3_for_date],
                         parameters=[self._request_file])

    def run(self):
        self.wait_for_completion()
