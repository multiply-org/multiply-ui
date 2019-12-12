import datetime
from .multiply_workflow import MultiplyMonitor


class PreprocessSar(MultiplyMonitor):

    def __init__(self, parameters):
        MultiplyMonitor.__init__(self,
                                 parameters,
                                 types=[('get_data_for_s1_preprocessing.py', 2), ('preprocess_s1.py', 2)])
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))

    def create_workflow(self):
        s1_slc = self._data_root + '/' + 's1_slc'
        s1_grd = self._data_root + '/' + 's1_grd'
        cursor = self._start
        while cursor <= self._stop:
            date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._step
            cursor -= self._one_day_step
            if cursor > self._stop:
                cursor = self._stop
            next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._one_day_step
            s1_slc_for_date =  s1_slc + '/' + date
            s1_grd_for_date =  s1_grd + '/' + date
            self.execute('get_data_for_s1_preprocessing.py', [], [s1_slc_for_date],
                         parameters=[self._request_file, date, next_date])
            self.execute('preprocess_s1.py', [s1_slc_for_date], [s1_grd_for_date],
                         parameters=[self._request_file, date, next_date])
