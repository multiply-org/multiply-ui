import datetime
from typing import Dict
from multiply_core.util import get_num_tiles
from multiply_workflow import MultiplyMonitor


class MultiplyFull(MultiplyMonitor):

    def __init__(self, parameters):
        MultiplyMonitor.__init__(self,
                                 parameters,
                                 types=[('data_access_get_static.py', 1), ('get_data_for_s2_preprocessing.py', 2),
                                        ('data_access_put_s2_l2.py', 1), ('retrieve_s2_priors.py', 2),
                                        ('preprocess_s2.py', 2), ('combine_hres_biophys_outputs.py', 1),
                                        ('infer_s2_kafka.py', 2), ('infer_s2_kaska.py', 2),
                                        ('get_data_for_s1_preprocessing.py', 1), ('preprocess_s1.py', 1),
                                        ('stack_s1.py', 2), ('determine_s1_priors.py', 2), ('infer_s1_kaska.py', 2)
                                        ]
                                 )
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))
        self._tile_width = parameters['General']['tile_width']
        self._tile_height = parameters['General']['tile_height']
        self._num_tiles_x = parameters['General']['num_tiles_x']
        self._num_tiles_y = parameters['General']['num_tiles_y']
        self._infer_s2_kafka = False
        self._infer_s2_kaska = False
        self._infer_s1_kaska = False
        for model in parameters['Inference']['forward_models']:
            if model['type'] == 'kafka' and model['data_type'] == 'Sentinel-2':
                self._infer_s2_kafka = True
            elif model['type'] == 'kaska' and model['data_type'] == 'Sentinel-2':
                self._infer_s2_kaska = True
            elif model['type'] == 'kaska' and model['data_type'] == 'Sentinel-1':
                self._infer_s1_kaska = True

    def create_workflow(self):
        start = datetime.datetime.strftime(self._start, '%Y-%m-%d')
        stop = datetime.datetime.strftime(self._stop, '%Y-%m-%d')
        params_dict = self._create_kafka_s2_inference_workflow(start, stop, {})
        params_dict = self._create_kaska_s2_inference_workflow(start, stop, params_dict)
        params_dict = self._create_kaska_s1_inference_workflow(start, stop, params_dict)
        # params_dict = self._create_eo_post_processing_workflow(start, stop, params_dict)
        # params_dict = self._create_variable_post_processing_workflow(start, stop, params_dict)

    def _create_kafka_s2_inference_workflow(self, start: str, stop: str, params_dict: Dict):
        if not self._infer_s2_kafka:
            return params_dict
        priors = self._data_root + '/' + 'priors'
        hres_state_dir = self._data_root + '/' + 'hresstate'
        modis = self._data_root + '/' + 'modis'
        cams = self._data_root + '/' + 'cams'
        s2 = self._data_root + '/' + 's2'
        sdrs = self._data_root + '/' + 'sdrs'
        provided_sdrs = self._data_root + '/' + 'provided_sdrs'
        hres_biophys_output = self._data_root + '/' + 'hresbiophys'
        emus = self._data_root + '/' + 'emus'
        dem = self._data_root + '/' + 'dem'
        self.execute('data_access_get_static.py', [], [emus, dem], parameters=[self._request_file, start, stop])
        cursor = self._start
        hres_state = 'none'
        hres_biophys_output_per_dates = []
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
            provided_sdrs_for_date = provided_sdrs + '/' + date
            self.execute('get_data_for_s2_preprocessing.py', [],
                         [modis_for_date, cams_for_date, s2_for_date, provided_sdrs_for_date],
                         parameters=[self._request_file, date, next_date])
            self.execute('preprocess_s2.py', [s2_for_date, modis_for_date, emus, cams_for_date, dem,
                                              provided_sdrs_for_date], [sdrs_for_date],
                         parameters=[self._request_file, date, next_date])
            #todo add asking whether preprocessing was performed on full tile
            self.execute('data_access_put_s2_l2.py', [sdrs_for_date, provided_sdrs_for_date], [],
                         parameters=[self._request_file, date, next_date])
            priors_for_date = priors + '/' + date
            self.execute('retrieve_s2_priors.py', [], [priors_for_date], parameters=[self._request_file, date, next_date])
            updated_state = hres_state_dir + '/' + date
            hres_biophys_output_per_date = hres_biophys_output + '/' + date
            hres_biophys_output_per_dates.append(hres_biophys_output_per_date)
            self.execute('infer_s2_kafka.py', [priors_for_date, sdrs_for_date],
                         [hres_biophys_output_per_date, updated_state],
                         parameters=[self._request_file, date, next_date, hres_state])
            hres_state = updated_state
        self.execute('combine_hres_biophys_outputs.py', hres_biophys_output_per_dates, [hres_biophys_output],
                     arameters=[self._request_file])
        params_dict['hres_biophys_output'] = hres_biophys_output
        return params_dict

    def _create_kaska_s2_inference_workflow(self, start: str, stop: str, params_dict: Dict):
        if not self._infer_s2_kaska:
            return params_dict
        modis = self._data_root + '/' + 'modis'
        cams = self._data_root + '/' + 'cams'
        s2 = self._data_root + '/' + 's2'
        emus = self._data_root + '/' + 'emus'
        dem = self._data_root + '/' + 'dem'
        priors = self._data_root + '/' + 'priors'
        provided_sdrs = self._data_root + '/' + 'provided_sdrs'
        sdrs = self._data_root + '/' + 'sdrs'
        hres_biophys_output = self._data_root + '/' + 'hresbiophys'
        self.execute('data_access_get_static.py', [], [emus, dem], parameters=[self._request_file, start, stop])
        self.execute('get_data_for_s2_preprocessing.py', [], [modis, cams, s2, provided_sdrs],
                     parameters=[self._request_file, start, stop])
        self.execute('preprocess_s2.py', [s2, modis, emus, cams, dem, provided_sdrs], [sdrs],
                     parameters=[self._request_file, start, stop])
        # todo add asking whether preprocessing was performed on full tile
        self.execute('data_access_put_s2_l2.py', [sdrs, provided_sdrs], [],
                     parameters=[self._request_file, start, stop])
        self.execute('retrieve_s2_priors.py', [], [priors], parameters=[self._request_file, start, stop])
        for tile_x in self._num_tiles_x:
            for tile_y in self._num_tiles_y:
                self.execute('infer-s2-kaska.py', [sdrs, priors], [hres_biophys_output],
                             parameters=[self._request_file, start, stop, tile_x, tile_y])
        params_dict['hres_biophys_output'] = hres_biophys_output
        return params_dict

    def _create_kaska_s1_inference_workflow(self, start: str, stop: str, params_dict: Dict):
        if not self._infer_s1_kaska:
            return params_dict
        s1_slc = self._data_root + '/' + 's1_slc'
        s1_grd = self._data_root + '/' + 's1_grd'
        s1_stack = self._data_root + '/' + 's1_stack'
        hres_biophys_output = params_dict['hres_biophys_output']
        s1_priors = self._data_root + '/' + 's1_priors'
        sar_biophys_output = self._data_root + '/' + 'sarbiophys'
        self.execute('get_data_for_s1_preprocessing.py', [], [s1_slc],
                     parameters=[self._request_file, start, stop])
        self.execute('preprocess_s1.py', [s1_slc], [s1_grd], parameters=[self._request_file, start, stop])
        cursor = self._start
        while cursor <= self._stop:
            date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._step
            next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            s1_stack_for_date = s1_stack + '/' + date
            self.execute('stack_s1.py', [s1_grd], [s1_stack_for_date],
                         parameters=[self._request_file, date, next_date])
            s1_priors_for_date = s1_priors + '/' + date
            self.execute('determine_s1_priors.py', [hres_biophys_output], [s1_priors_for_date],
                         parameters=[self._request_file, date, next_date])
            for tile_x in self._num_tiles_x:
                for tile_y in self._num_tiles_y:
                    self.execute('infer-s1-kaska.py', [s1_stack_for_date, s1_priors], [sar_biophys_output],
                                 parameters=[self._request_file, date, next_date, tile_x, tile_y])
        return params_dict

    # def _create_eo_post_processing_workflow(self, start: str, stop: str, params_dict: Dict):
    #         eo_indicators = self._data_root + '/' + 'eo_indicators'
    #         cursor = self._start
    #         while cursor <= self._stop:
    #             date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
    #             cursor += self._step
    #             next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
    #             eo_indicators_for_date = eo_indicators + '/' + date
    #             self.execute('post_process_s2.py', [sdrs | sdrs_for_date], [eo_indicators_for_date],
    #                              parameters=[self._request_file, date, next_date])


    # def _create_variable_post_processing_workflow(self, start: str, stop: str, params_dict: Dict):
    #         eo_indicators = self._data_root + '/' + 'eo_indicators'
    #         variable_indicators = self._data_root + '/' + 'variable_indicators'
    #         cursor = self._start
    #         while cursor <= self._stop:
    #             date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
    #             cursor += self._step
    #             next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
    #             variable_indicators_for_date = variable_indicators + '/' + date
    #             self.execute('post_process_variables.py', [hres_biophys_output | sar_biophys_output],
    #                          [variable_indicators_for_date], parameters=[self._request_file, date, next_date])
