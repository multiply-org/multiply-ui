import datetime
import logging
from pmonitor import PMonitor


logging.getLogger().setLevel(logging.INFO)


class OnlyGetData(PMonitor):

    def __init__(self, parameters):
        PMonitor.__init__(self,
                          ['none', parameters['data_root']],
                          request=parameters['requestName'],
                          hosts=[('localhost',10)],
                          types=[('data_access_get_static.py',1), ('data_access_get_dynamic.py', 2)],
                          logdir=parameters['log_dir'],
                          simulation='simulation' in parameters and parameters['simulation'])
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))
        self._tasks_progress = {}

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

    def _observe_step(self, call, inputs, outputs, parameters, code):
        if code > 0:
            return
        if self._script:
            command = '{0} {1} {2} {3} {4}'.format(self._path_of_call(self._script), call, ' '.join(parameters),
                                                   ' '.join(inputs), ' '.join(outputs))
        else:
            command = '{0} {1} {2} {3}'.format(self._path_of_call(call), ' '.join(parameters), ' '.join(inputs),
                                               ' '.join(outputs))
        print(f'observing {command}')
        self._commands.add(command)

    def _run_step(self, task_id, host, command, output_paths, log_prefix, async_):
        """
        Executes command on host, collects output paths if any, returns exit code
        """
        logging.info(f'task_id {task_id}')
        logging.info(f'host {host}')
        logging.info(f'command {command}')
        logging.info(f'output_paths {output_paths}')
        wd = self._prepare_working_dir(task_id)
        logging.info(f'wd {wd}')
        process = PMonitor._start_processor(command, host, wd)
        self._trace_processor_output(output_paths, process, task_id, command, wd, log_prefix, async_)
        process.stdout.close()
        code = process.wait()
        # if code == 0 and not async_ and not self._cache is None and 'cache' in wd:
        #     subprocess.call(['rm', '-rf', wd])
        return code

    
    def _trace_processor_output(self, output_paths, process, task_id, command, wd, log_prefix, async_):
        """
        traces processor output, recognises 'output=' lines, writes all lines to trace file in working dir.
        for async calls reads external ID from stdout.
        """
        if self._cache is None or self._logdir != '.':
            trace = open('{0}/{1}-{2:04d}.out'.format(self._logdir, log_prefix, task_id), 'w')
        else:
            trace = open('{0}/{1}-{2:04d}.out'.format(wd, log_prefix, task_id), 'w')
        line = None
        for l in process.stdout:
            line = l.decode()
            if line.startswith('output='):
                output_paths.append(line[7:].strip())
            elif line.startswith('progress='):
                self._tasks_progress[command] = line[9:].strip()
            trace.write(line)
            trace.flush()
        trace.close()
        if async_ and line:
            # assumption that last line contains external ID, with stderr mixed with stdout
            output_paths[:] = []
            output_paths.append(line.strip())
    
    def get_progress(self, command):
        if command in self._tasks_progress:
            return int(self._tasks_progress[command])
        return 0

    def run(self):
        self.wait_for_completion()
