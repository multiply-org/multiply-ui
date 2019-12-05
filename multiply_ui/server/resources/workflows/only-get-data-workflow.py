import datetime
from .multiply_workflow import MultiplyMonitor


class OnlyGetData(MultiplyMonitor):

    def __init__(self, parameters):
        MultiplyMonitor.__init__(self,
                                 parameters,
                                 types=[('data_access_get_static.py', 1), ('data_access_get_dynamic.py', 2)])
                          # ['none', parameters['data_root']],
                          # request=parameters['requestName'],
                          # hosts=[('localhost', 10)],
                          # types=[('data_access_get_static.py', 1), ('data_access_get_dynamic.py', 2)],
                          # logdir=parameters['log_dir'],
                          # simulation='simulation' in parameters and parameters['simulation'])
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))

    def create_workflow(self):
        modis = self._data_root + '/' + 'modis'
        cams = self._data_root + '/' + 'cams'
        s2 = self._data_root + '/' + 's2'
        emus = self._data_root + '/' + 'emus'
        dem = self._data_root + '/' + 'dem'

        start = datetime.datetime.strftime(self._start, '%Y-%m-%d')
        stop = datetime.datetime.strftime(self._stop, '%Y-%m-%d')
        self.execute('data_access_get_static.py', [], [emus, dem], parameters=[self._request_file, start, stop])
        cursor = self._start
        while cursor <= self._stop:
            date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._step
            cursor -= self._one_day_step
            if cursor > self._stop:
                cursor = self._stop
            next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._one_day_step

            modis_for_date = modis + '/' + date
            cams_for_date = cams + '/' + date
            s2_for_date = s2 + '/' + date
            self.execute('data_access_get_dynamic.py', [], [modis_for_date, cams_for_date, s2_for_date],
                         parameters=[self._request_file, date, next_date])
