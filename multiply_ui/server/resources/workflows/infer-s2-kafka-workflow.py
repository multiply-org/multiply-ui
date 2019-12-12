import datetime
from .multiply_workflow import MultiplyMonitor


class InferS2Kafka(MultiplyMonitor):

    def __init__(self, parameters):
        MultiplyMonitor.__init__(self,
                          parameters,
                          types=[('data_access_get_static.py', 1), ('get_data_for_s2_preprocessing.py', 2),
                                 ('data_access_put_s2_l2.py', 1), ('retrieve_s2_priors.py', 2), ('preprocess_s2.py', 2),
                                 ('infer_s2_kafka.py', 2)]
                          )
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))

    def create_workflow(self):
        priors = self._data_root + '/' + 'priors'
        hres_state_dir = self._data_root + '/' + 'hresstate'
        modis = self._data_root + '/' + 'modis'
        cams = self._data_root + '/' + 'cams'
        s2 = self._data_root + '/' + 's2'
        sdrs = self._data_root + '/' + 'sdrs'
        hres_biophys_output = self._data_root + '/' + 'hresbiophys'
        emus = self._data_root + '/' + 'emus'
        dem = self._data_root + '/' + 'dem'

        start = datetime.datetime.strftime(self._start, '%Y-%m-%d')
        stop = datetime.datetime.strftime(self._stop, '%Y-%m-%d')
        self.execute('data_access_get_static.py', [], [emus, dem], parameters=[self._request_file, start, stop])

        cursor = self._start
        hres_state = 'none'
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
            sdrs_for_date = sdrs + '/' + date
            self.execute('get_data_for_s2_preprocessing.py', [], [modis_for_date, cams_for_date, s2_for_date],
                         parameters=[self._request_file, date, next_date])
            self.execute('preprocess_s2.py', [s2_for_date, modis_for_date, emus, cams_for_date, dem], [sdrs_for_date],
                         parameters=[self._request_file, date, next_date])
            # self.execute('data_access_put_s2_l2.py', [sdrs_for_date], [], parameters=[])

            priors_for_date = priors + '/' + date
            self.execute('retrieve_s2_priors.py', [], [priors_for_date], parameters=[self._request_file, date, next_date])
            updated_state = hres_state_dir + '/' + date
            self.execute('infer_s2_kafka.py', [priors_for_date, sdrs_for_date], [hres_biophys_output, updated_state],
                         parameters=[self._request_file, date, next_date, hres_state])
            hres_state = updated_state
