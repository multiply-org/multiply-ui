import datetime
from .multiply_workflow import MultiplyMonitor


class InferS2Kafka(MultiplyMonitor):

    def __init__(self, parameters):
        MultiplyMonitor.__init__(self,
                                 parameters,
                                 types=[('data_access_get_static.py', 1), ('data_access_get_dynamic.py', 2),
                                        ('data_access_put_s2_l2.py', 1), ('retrieve_priors.py', 2),
                                        ('preprocess_s2.py', 2),
                                        ('infer_s2_kafka.py', 2)]
                                 )
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))
        self._types = parameters['types']

    def create_workflow(self):
        start = datetime.datetime.strftime(self._start, '%Y-%m-%d')
        stop = datetime.datetime.strftime(self._stop, '%Y-%m-%d')

        if 'preprocess_s2.py' in self._types:
            emus = self._data_root + '/' + 'emus'
            dem = self._data_root + '/' + 'dem'
            self.execute('data_access_get_static.py', [], [emus, dem], parameters=[self._request_file, start, stop])
            modis = self._data_root + '/' + 'modis'
            cams = self._data_root + '/' + 'cams'
            s2 = self._data_root + '/' + 's2'
            sdrs = self._data_root + '/' + 'sdrs'
        if 'retrieve_priors.py' in self._types:
            priors = self._data_root + '/' + 'priors'
        if 'infer_s2_kafka.py' in self._types:
            hres_state = 'none'
            hres_state_dir = self._data_root + '/' + 'hresstate'
            hres_biophys_output = self._data_root + '/' + 'hresbiophys'

        cursor = self._start
        while cursor <= self._stop:
            date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._step
            cursor -= self._one_day_step
            if cursor > self._stop:
                cursor = self._stop
            next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._one_day_step

            if 'preprocess_s2.py' in self._types:
                modis_for_date = modis + '/' + date
                cams_for_date = cams + '/' + date
                s2_for_date = s2 + '/' + date
                sdrs_for_date = sdrs + '/' + date
                self.execute('data_access_get_dynamic.py', [], [modis_for_date, cams_for_date, s2_for_date],
                             parameters=[self._request_file, date, next_date])
                self.execute('preprocess_s2.py', [s2_for_date, modis_for_date, emus, cams_for_date, dem],
                             [sdrs_for_date], parameters=[self._request_file, date, next_date])
            if 'retrieve_priors.py' in self._types:
                priors_for_date = priors + '/' + date
                self.execute('retrieve_priors.py', [], [priors_for_date],
                             parameters=[self._request_file, date, next_date])
                updated_state = hres_state_dir + '/' + date
            if 'infer_s2_kafka.py' in self._types:
                self.execute('infer_s2_kafka.py', [priors_for_date, sdrs_for_date],
                             [hres_biophys_output, updated_state],
                             parameters=[self._request_file, date, next_date, hres_state])
                hres_state = updated_state
        if 'infer-s1-kaska.py' in self._types:
            s1_slc = self._data_root + '/' + 's1_slc'
            s1_grd = self._data_root + '/' + 's1_slc'
            sar_biophys_output = self._data_root + '/' + 'sar_biophys_output'
            self.execute('data_access_get_s1.py', [], [s1_slc],
                         parameters=[self._request_file, date, next_date])
        if 'infer-s2-kaska.py' in self._types:
            self.execute('data_access_get_dynamic.py', [], [modis, cams, s2],
                         parameters=[self._request_file, start, stop])
            # if not s2-preprocess-per-aoi:
            #     self.execute('preprocess_s2.py', [s2_for_date, modis_for_date, emus, cams_for_date, dem],
            #                  [sdrs_for_date], parameters=[self._request_file, date, next_date])
        if 'infer-s1-kaska.py' in self._types or 'infer-s2-kaska.py' in self._types:
            # determine tiling
            for tile in tiles:
                # if s2-preprocess-per-aoi:
                #     self.execute('preprocess_s2.py', [s2_for_date, modis, emus, cams, dem],
                #                  [sdrs], parameters=[self._request_file, start, stop])
                if 'retrieve_priors.py' in self._types:
                    self.execute('retrieve_priors.py', [], [priors],
                                 parameters=[self._request_file, start, stop])
                if 'infer-s2-kaska.py' in self._types:
                    self.execute('infer-s2-kaska.py', [sdrs, priors], [hres_biophys_output],
                                 parameters=[self._request_file, start, stop])
                # combine priors from priors and hres_biophys_output to s1_priors
                if 'infer-s1-kaska.py' in self._types:
                    self.execute('preprocess_s1.py', [s1_slc], [s1_grd],
                                 parameters=[self._request_file, start, stop])
                    self.execute('infer-s1-kaska.py', [s1_grd, s1_priors], [sar_biophys_output],
                                 parameters=[self._request_file, start, stop])
        if 'post_process_s2.py' in self._types:
            eo_indicators = self._data_root + '/' + 'eo_indicators'
        if 'post_process_variables.py' in self._types:
            variable_indicators = self._data_root + '/' + 'variable_indicators'
        if 'post_process_s2.py' in self._types or 'post_process_variables.py' in self._types:
            cursor = self._start
            while cursor <= self._stop:
                date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
                next_date += self._step
                if 'post_process_s2.py' in self._types:
                    eo_indicators_for_date = eo_indicators + '/' + date
                    self.execute('post_process_s2.py', [sdrs | sdrs_for_date], [eo_indicators_for_date],
                                 parameters=[self._request_file, date, next_date])
                if 'post_process_variables.py' in self._types:
                    variable_indicators_for_date = variable_indicators + '/' + date
                    self.execute('post_process_variables.py', [hres_biophys_output | sar_biophys_output],
                                 [variable_indicators_for_date], parameters=[self._request_file, date, next_date])


        priors = self._data_root + '/' + 'priors'
        modis = self._data_root + '/' + 'modis'
        cams = self._data_root + '/' + 'cams'
        s2 = self._data_root + '/' + 's2'
        emus = self._data_root + '/' + 'emus'
        dem = self._data_root + '/' + 'dem'
        sdrs = self._data_root + '/' + 'sdrs'
        hres_state_dir = self._data_root + '/' + 'hresstate'
        hres_biophys_output = self._data_root + '/' + 'hresbiophys'

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
            self.execute('data_access_get_dynamic.py', [], [modis_for_date, cams_for_date, s2_for_date],
                         parameters=[self._request_file, date, next_date])
            self.execute('preprocess_s2.py', [s2_for_date, modis_for_date, emus, cams_for_date, dem], [sdrs_for_date],
                         parameters=[self._request_file, date, next_date])
            # self.execute('data_access_put_s2_l2.py', [sdrs_for_date], [], parameters=[])

            priors_for_date = priors + '/' + date
            self.execute('retrieve_priors.py', [], [priors_for_date], parameters=[self._request_file, date, next_date])
            updated_state = hres_state_dir + '/' + date
            self.execute('infer_s2_kafka.py', [priors_for_date, sdrs_for_date], [hres_biophys_output, updated_state],
                         parameters=[self._request_file, date, next_date, hres_state])
            hres_state = updated_state

    def _set_up_dirs(self):
        if 'retrieve_priors.py' in self._types:
            self._priors = self._data_root + '/' + 'priors'
        if 'data_access_get_dynamic.py' in self._types:
            self._modis = self._data_root + '/' + 'modis'
            self._cams = self._data_root + '/' + 'cams'
            self._s2 = self._data_root + '/' + 's2'

    def create_workflow(self):
        priors = self._data_root + '/' + 'priors'
        modis = self._data_root + '/' + 'modis'
        cams = self._data_root + '/' + 'cams'
        s2 = self._data_root + '/' + 's2'
        emus = self._data_root + '/' + 'emus'
        dem = self._data_root + '/' + 'dem'
        sdrs = self._data_root + '/' + 'sdrs'
        hres_state_dir = self._data_root + '/' + 'hresstate'
        hres_biophys_output = self._data_root + '/' + 'hresbiophys'

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
            self.execute('data_access_get_dynamic.py', [], [modis_for_date, cams_for_date, s2_for_date],
                         parameters=[self._request_file, date, next_date])
            self.execute('preprocess_s2.py', [s2_for_date, modis_for_date, emus, cams_for_date, dem], [sdrs_for_date],
                         parameters=[self._request_file, date, next_date])
            # self.execute('data_access_put_s2_l2.py', [sdrs_for_date], [], parameters=[])

            priors_for_date = priors + '/' + date
            self.execute('retrieve_priors.py', [], [priors_for_date], parameters=[self._request_file, date, next_date])
            updated_state = hres_state_dir + '/' + date
            self.execute('infer_s2_kafka.py', [priors_for_date, sdrs_for_date], [hres_biophys_output, updated_state],
                         parameters=[self._request_file, date, next_date, hres_state])
            hres_state = updated_state
