import datetime
import os
import signal
from pmonitor import PMonitor


class OnlyGetPriors(PMonitor):

    def __init__(self, parameters):
        PMonitor.__init__(self,
                          ['none', parameters['data_root']],
                          request=parameters['requestName'],
                          hosts=[('localhost', 10)],
                          types=[('retrieve_priors.py', 2)],
                          logdir=parameters['log_dir'],
                          simulation='simulation' in parameters and parameters['simulation'])
        self._data_root = parameters['data_root']
        self._request_file = parameters['requestFile']
        self._start = datetime.datetime.strptime(str(parameters['General']['start_time']), '%Y-%m-%d')
        self._stop = datetime.datetime.strptime(str(parameters['General']['end_time']), '%Y-%m-%d')
        self._one_day_step = datetime.timedelta(days=1)
        self._step = datetime.timedelta(days=int(str(parameters['Inference']['time_interval'])))
        self._tasks_progress = {}
        self._lower_script_progress = {}
        self._upper_script_progress = {}
        self._processor_logs = {}
        self._pids = {}

    def create_workflow(self):
        priors = self._data_root + '/' + 'priors'

        cursor = self._start
        while cursor <= self._stop:
            date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._step
            cursor -= self._one_day_step
            if cursor > self._stop:
                cursor = self._stop
            next_date = datetime.datetime.strftime(cursor, '%Y-%m-%d')
            cursor += self._one_day_step
            priors_for_date = priors + '/' + date
            self.execute('retrieve_priors.py', [], [priors_for_date], parameters=[self._request_file, date, next_date])

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
        wd = self._prepare_working_dir(task_id)
        process = PMonitor._start_processor(command, host, wd)
        self._pids[command] = process.pid
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
        if command not in self._processor_logs:
            self._processor_logs[command] = []
        for l in process.stdout:
            line = l.decode()
            if line.startswith('output='):
                output_paths.append(line[7:].strip())
            elif line.startswith('INFO:ScriptProgress'):
                script_progress = line.split(':')[-1].split('-')
                self._lower_script_progress[command] = int(script_progress[0])
                self._upper_script_progress[command] = int(script_progress[1])
                self._tasks_progress[command] = int(script_progress[0])
            elif line.startswith('INFO:ComponentProgress'):
                component_progress = line.split(':')[-1]
                if command in self._upper_script_progress and command in self._lower_script_progress:
                    progress_diff = float(self._upper_script_progress[command] - self._lower_script_progress[command])
                    relative_progress = int((float(component_progress) * progress_diff) / 100.0)
                    self._tasks_progress[command] = self._lower_script_progress[command] + relative_progress
            else:
                self._processor_logs[command].append(line)
            trace.write(line)
            trace.flush()
        trace.close()
        if async_ and line:
            # assumption that last line contains external ID, with stderr mixed with stdout
            output_paths[:] = []
            output_paths.append(line.strip())

    def get_progress(self, command):
        if command in self._tasks_progress:
            return self._tasks_progress[command]
        return 0

    def get_logs(self, command):
        if command in self._processor_logs:
            return self._processor_logs[command]
        return []

    def run(self):
        return self.wait_for_completion()

    def cancel(self):
        self._canceled = True
        for pid in self._pids:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
