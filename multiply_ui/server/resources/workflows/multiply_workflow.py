import logging
import os
import signal
import sys
from pmonitor import PMonitor

logging.getLogger().setLevel(logging.INFO)


class MultiplyMonitor(PMonitor):

    def __init__(self, parameters, types):
        PMonitor.__init__(self,
                          ['none', parameters['data_root']],
                          request=parameters['requestName'],
                          hosts=[('localhost', 10)],
                          types=types,
                          logdir=parameters['log_dir'],
                          simulation='simulation' in parameters and parameters['simulation'])
        self._tasks_progress = {}
        self._lower_script_progress = {}
        self._upper_script_progress = {}
        self._processor_logs = {}
        self._pids = {}
        self._to_be_cancelled = []
        self._cancelled = []

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
        code = self.wait_for_completion()
        if len(self._cancelled) > 0:
            return -1
        return code

    def cancel(self):
        for pid in self._pids:
            try:
                os.kill(self._pids[pid], signal.SIGTERM)
                logging.info(f'Cancelling {pid}')
                self._to_be_cancelled.append(pid)
            except ProcessLookupError:
                # okay, process was outdated
                continue

    def _write_status(self, with_backlog=False):
        self._status.seek(0)
        self._status.write('{0} created, {1} running, {2} backlog, {3} processed, {4} failed, {5} cancelled\n'. \
                           format(self._created, len(self._running), len(self._backlog), self._processed,
                                  len(self._failed), len(self._cancelled)))

        for l in self._failed:
            self._status.write('f {0}\n'.format(l))
        for l in self._cancelled:
            self._status.write('c {0}\n'.format(l))
        for l in self._running:
            if isinstance(self._running[l], PMonitor.Args):
                self._status.write('r [{0}] {1}\n'.format(self._running[l].external_id, l))
            elif isinstance(self._running[l], str):
                self._status.write('r [{0}] {1}\n'.format(self._running[l], l))
            else:
                self._status.write('r {0}\n'.format(l))
        if with_backlog:
            for r in self._backlog:
                self._status.write('b {0} {1} {2} {3}\n'.format(PMonitor.Args.get_call(r.args),
                                                                ' '.join(PMonitor.Args.get_parameters(r.args)),
                                                                ' '.join(PMonitor.Args.get_inputs(r.args)),
                                                                ' '.join(PMonitor.Args.get_outputs(r.args))))
        self._status.truncate()
        self._status.flush()

    def _finalise_step(self, call, code, command, host, output_paths, outputs, typeOnly=False):
        """
        releases host and type resources, updates report, schedules mature steps, handles failure
        """
        with self._mutex:
            self._release_constraint(call, host, typeOnly=typeOnly)
            self._running.pop(command)
            if code == 0:
                self._report.write(command + '\n')
                self._report_and_bind_outputs(outputs, output_paths)
                self._report.flush()
                self._processed += 1
            elif command in self._to_be_cancelled:
                self._cancelled.append(command)
                sys.__stderr__.write('cancelled {0}\n'.format(command))
            else:
                self._failed.append(command)
                sys.__stderr__.write('failed {0}\n'.format(command))
            self._check_for_mature_tasks()
