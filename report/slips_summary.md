# Potential Slip Report

Total calls analyzed: 11574

## Status counts

- unresolved: 6603
- ok_builtin: 2643
- ok: 1312
- ok_stdlib: 1004
- variadic: 10
- argument_mismatch: 2

Potential slips (argument mismatch or unresolved): 6605

## Detailed slip entries

- check_architecture.py:11 in `None` -> `sys.path.insert` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `sys.path.insert`
  - Target info: {'type': 'unresolved', 'module_path': 'sys.path', 'func_name': 'insert', 'expression': 'sys.path.insert'}

- check_architecture.py:22 in `main` -> `architecture_checker.ArchitectureChecker` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ArchitectureChecker`
  - Target info: {'type': 'unresolved', 'module_path': 'architecture_checker', 'func_name': 'ArchitectureChecker', 'expression': 'ArchitectureChecker'}

- check_architecture.py:28 in `main` -> `check_architecture.report.has_errors` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `report.has_errors`
  - Target info: {'type': 'unresolved', 'module_path': 'check_architecture', 'func_name': 'report.has_errors', 'expression': 'report.has_errors'}

- opencli.py:21 in `None` -> `sys.path.insert` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `sys.path.insert`
  - Target info: {'type': 'unresolved', 'module_path': 'sys.path', 'func_name': 'insert', 'expression': 'sys.path.insert'}

- advanced_profiler.py:30 in `None` -> `matplotlib.use` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `matplotlib.use`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib', 'func_name': 'use', 'expression': 'matplotlib.use'}

- advanced_profiler.py:42 in `None` -> `matplotlib.use` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `matplotlib.use`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib', 'func_name': 'use', 'expression': 'matplotlib.use'}

- advanced_profiler.py:88 in `AdvancedProfiler._categorize_thread` -> `advanced_profiler.thread_name.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `thread_name.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'thread_name.lower', 'expression': 'thread_name.lower'}

- advanced_profiler.py:91 in `AdvancedProfiler._categorize_thread` -> `advanced_profiler.pattern.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `pattern.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'pattern.lower', 'expression': 'pattern.lower'}

- advanced_profiler.py:95 in `AdvancedProfiler._categorize_thread` -> `advanced_profiler.pattern.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `pattern.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'pattern.lower', 'expression': 'pattern.lower'}

- advanced_profiler.py:105 in `AdvancedProfiler.capture_sample` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `datetime.now().isoformat`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'datetime.now().isoformat'}

- advanced_profiler.py:110 in `AdvancedProfiler.capture_sample` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `sys._current_frames().items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'sys._current_frames().items'}

- advanced_profiler.py:131 in `AdvancedProfiler.capture_sample` -> `advanced_profiler.current_frame.filename.split` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `current_frame.filename.split`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'current_frame.filename.split', 'expression': 'current_frame.filename.split'}

- advanced_profiler.py:135 in `AdvancedProfiler.capture_sample` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `stack[-2].filename.split`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'stack[-2].filename.split'}

- advanced_profiler.py:155 in `AdvancedProfiler.capture_sample` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `sample['threads'].append`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': "sample['threads'].append"}

- advanced_profiler.py:158 in `AdvancedProfiler.capture_sample` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.function_timeline[func_id].append`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.function_timeline[func_id].append'}

- advanced_profiler.py:162 in `AdvancedProfiler.capture_sample` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.call_graph[caller_id].append`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.call_graph[caller_id].append'}

- advanced_profiler.py:184 in `AdvancedProfiler.profile` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.samples.append`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.samples.append'}

- advanced_profiler.py:218 in `AdvancedProfiler.analyze` -> `advanced_profiler.function_calls.items` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `function_calls.items`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'function_calls.items', 'expression': 'function_calls.items'}

- advanced_profiler.py:225 in `AdvancedProfiler.analyze` -> `advanced_profiler.thread_activity.items` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `thread_activity.items`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'thread_activity.items', 'expression': 'thread_activity.items'}

- advanced_profiler.py:233 in `AdvancedProfiler.analyze` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.call_graph.values`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.call_graph.values'}

- advanced_profiler.py:238 in `AdvancedProfiler.analyze` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.call_graph.items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.call_graph.items'}

- advanced_profiler.py:240 in `AdvancedProfiler.analyze` -> `advanced_profiler.handoffs.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `handoffs.append`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'handoffs.append', 'expression': 'handoffs.append'}

- advanced_profiler.py:244 in `AdvancedProfiler.analyze` -> `advanced_profiler.handoff_counts.most_common` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `handoff_counts.most_common`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'handoff_counts.most_common', 'expression': 'handoff_counts.most_common'}

- advanced_profiler.py:259 in `AdvancedProfiler.generate_pdf_timeline` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.function_timeline.keys`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.function_timeline.keys'}

- advanced_profiler.py:263 in `AdvancedProfiler.generate_pdf_timeline` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `functions_by_role[role].append`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'functions_by_role[role].append'}

- advanced_profiler.py:266 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.pyplot.subplots` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `plt.subplots`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.pyplot', 'func_name': 'subplots', 'expression': 'plt.subplots'}

- advanced_profiler.py:287 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.patches.Rectangle` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `mpatches.Rectangle`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.patches', 'func_name': 'Rectangle', 'expression': 'mpatches.Rectangle'}

- advanced_profiler.py:296 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.add_patch` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.add_patch`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.add_patch', 'expression': 'ax.add_patch'}

- advanced_profiler.py:298 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.y_labels.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `y_labels.append`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'y_labels.append', 'expression': 'y_labels.append'}

- advanced_profiler.py:298 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.func_id.split` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `func_id.split`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'func_id.split', 'expression': 'func_id.split'}

- advanced_profiler.py:299 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.y_ticks.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `y_ticks.append`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'y_ticks.append', 'expression': 'y_ticks.append'}

- advanced_profiler.py:302 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.role_boundaries.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `role_boundaries.append`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'role_boundaries.append', 'expression': 'role_boundaries.append'}

- advanced_profiler.py:306 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.axhline` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.axhline`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.axhline', 'expression': 'ax.axhline'}

- advanced_profiler.py:308 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.text` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.text`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.text', 'expression': 'ax.text'}

- advanced_profiler.py:313 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.set_xlim` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.set_xlim`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.set_xlim', 'expression': 'ax.set_xlim'}

- advanced_profiler.py:314 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.set_ylim` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.set_ylim`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.set_ylim', 'expression': 'ax.set_ylim'}

- advanced_profiler.py:315 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.set_xlabel` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.set_xlabel`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.set_xlabel', 'expression': 'ax.set_xlabel'}

- advanced_profiler.py:316 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.set_ylabel` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.set_ylabel`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.set_ylabel', 'expression': 'ax.set_ylabel'}

- advanced_profiler.py:317 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.set_yticks` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.set_yticks`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.set_yticks', 'expression': 'ax.set_yticks'}

- advanced_profiler.py:318 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.set_yticklabels` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.set_yticklabels`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.set_yticklabels', 'expression': 'ax.set_yticklabels'}

- advanced_profiler.py:319 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.set_title` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.set_title`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.set_title', 'expression': 'ax.set_title'}

- advanced_profiler.py:325 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.grid` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.grid`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.grid', 'expression': 'ax.grid'}

- advanced_profiler.py:329 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.patches.Patch` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `mpatches.Patch`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.patches', 'func_name': 'Patch', 'expression': 'mpatches.Patch'}

- advanced_profiler.py:330 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.patches.Patch` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `mpatches.Patch`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.patches', 'func_name': 'Patch', 'expression': 'mpatches.Patch'}

- advanced_profiler.py:331 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.patches.Patch` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `mpatches.Patch`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.patches', 'func_name': 'Patch', 'expression': 'mpatches.Patch'}

- advanced_profiler.py:333 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.ax.legend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ax.legend`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'ax.legend', 'expression': 'ax.legend'}

- advanced_profiler.py:336 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.pyplot.tight_layout` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `plt.tight_layout`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.pyplot', 'func_name': 'tight_layout', 'expression': 'plt.tight_layout'}

- advanced_profiler.py:337 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.backends.backend_pdf.PdfPages` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `PdfPages`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.backends.backend_pdf', 'func_name': 'PdfPages', 'expression': 'PdfPages'}

- advanced_profiler.py:338 in `AdvancedProfiler.generate_pdf_timeline` -> `advanced_profiler.pdf.savefig` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `pdf.savefig`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'pdf.savefig', 'expression': 'pdf.savefig'}

- advanced_profiler.py:339 in `AdvancedProfiler.generate_pdf_timeline` -> `matplotlib.pyplot.close` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `plt.close`
  - Target info: {'type': 'unresolved', 'module_path': 'matplotlib.pyplot', 'func_name': 'close', 'expression': 'plt.close'}

- advanced_profiler.py:353 in `AdvancedProfiler.save_raw_data` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.call_graph.items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.call_graph.items'}

- advanced_profiler.py:354 in `AdvancedProfiler.save_raw_data` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.function_timeline.items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.function_timeline.items'}

- advanced_profiler.py:368 in `main` -> `advanced_profiler.parser.add_argument` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parser.add_argument`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'parser.add_argument', 'expression': 'parser.add_argument'}

- advanced_profiler.py:370 in `main` -> `advanced_profiler.parser.add_argument` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parser.add_argument`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'parser.add_argument', 'expression': 'parser.add_argument'}

- advanced_profiler.py:372 in `main` -> `advanced_profiler.parser.add_argument` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parser.add_argument`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'parser.add_argument', 'expression': 'parser.add_argument'}

- advanced_profiler.py:374 in `main` -> `advanced_profiler.parser.parse_args` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parser.parse_args`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'parser.parse_args', 'expression': 'parser.parse_args'}

- advanced_profiler.py:377 in `main` -> `advanced_profiler.AdvancedProfiler` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `AdvancedProfiler`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'AdvancedProfiler', 'expression': 'AdvancedProfiler'}

- inject_advanced_profiler.py:20 in `None` -> `sys.path.insert` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `sys.path.insert`
  - Target info: {'type': 'unresolved', 'module_path': 'sys.path', 'func_name': 'insert', 'expression': 'sys.path.insert'}

- inject_advanced_profiler.py:20 in `None` -> `os.path.dirname` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `os.path.dirname`
  - Target info: {'type': 'unresolved', 'module_path': 'os.path', 'func_name': 'dirname', 'expression': 'os.path.dirname'}

- inject_advanced_profiler.py:20 in `None` -> `os.path.abspath` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `os.path.abspath`
  - Target info: {'type': 'unresolved', 'module_path': 'os.path', 'func_name': 'abspath', 'expression': 'os.path.abspath'}

- inject_advanced_profiler.py:42 in `inject_and_profile` -> `advanced_profiler.AdvancedProfiler` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `AdvancedProfiler`
  - Target info: {'type': 'unresolved', 'module_path': 'advanced_profiler', 'func_name': 'AdvancedProfiler', 'expression': 'AdvancedProfiler'}

- inject_advanced_profiler.py:47 in `inject_and_profile.profile_thread` -> `inject_advanced_profiler.profiler.profile` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `profiler.profile`
  - Target info: {'type': 'unresolved', 'module_path': 'inject_advanced_profiler', 'func_name': 'profiler.profile', 'expression': 'profiler.profile'}

- inject_advanced_profiler.py:48 in `inject_and_profile.profile_thread` -> `inject_advanced_profiler.profiler.analyze` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `profiler.analyze`
  - Target info: {'type': 'unresolved', 'module_path': 'inject_advanced_profiler', 'func_name': 'profiler.analyze', 'expression': 'profiler.analyze'}

- inject_advanced_profiler.py:49 in `inject_and_profile.profile_thread` -> `inject_advanced_profiler.profiler.generate_pdf_timeline` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `profiler.generate_pdf_timeline`
  - Target info: {'type': 'unresolved', 'module_path': 'inject_advanced_profiler', 'func_name': 'profiler.generate_pdf_timeline', 'expression': 'profiler.generate_pdf_timeline'}

- inject_advanced_profiler.py:50 in `inject_and_profile.profile_thread` -> `inject_advanced_profiler.profiler.save_raw_data` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `profiler.save_raw_data`
  - Target info: {'type': 'unresolved', 'module_path': 'inject_advanced_profiler', 'func_name': 'profiler.save_raw_data', 'expression': 'profiler.save_raw_data'}

- inject_advanced_profiler.py:64 in `inject_and_profile` -> `inject_advanced_profiler.thread.start` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `thread.start`
  - Target info: {'type': 'unresolved', 'module_path': 'inject_advanced_profiler', 'func_name': 'thread.start', 'expression': 'thread.start'}

- thread_analyzer.py:45 in `ThreadAnalyzer._categorize_thread` -> `thread_analyzer.thread_name.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `thread_name.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'thread_name.lower', 'expression': 'thread_name.lower'}

- thread_analyzer.py:49 in `ThreadAnalyzer._categorize_thread` -> `thread_analyzer.pattern.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `pattern.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'pattern.lower', 'expression': 'pattern.lower'}

- thread_analyzer.py:54 in `ThreadAnalyzer._categorize_thread` -> `thread_analyzer.pattern.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `pattern.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'pattern.lower', 'expression': 'pattern.lower'}

- thread_analyzer.py:109 in `ThreadAnalyzer.capture_snapshot` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `datetime.now().isoformat`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'datetime.now().isoformat'}

- thread_analyzer.py:114 in `ThreadAnalyzer.capture_snapshot` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `sys._current_frames().items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'sys._current_frames().items'}

- thread_analyzer.py:141 in `ThreadAnalyzer.capture_snapshot` -> `thread_analyzer.thread_obj.is_alive` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `thread_obj.is_alive`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'thread_obj.is_alive', 'expression': 'thread_obj.is_alive'}

- thread_analyzer.py:161 in `ThreadAnalyzer.capture_snapshot` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `snapshot['threads'].append`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': "snapshot['threads'].append"}

- thread_analyzer.py:168 in `ThreadAnalyzer.capture_snapshot` -> `thread_analyzer.loop.is_closed` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `loop.is_closed`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'loop.is_closed', 'expression': 'loop.is_closed'}

- thread_analyzer.py:177 in `ThreadAnalyzer.capture_snapshot` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.snapshots.append`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.snapshots.append'}

- thread_analyzer.py:244 in `ThreadAnalyzer._is_thread_blocked` -> `thread_analyzer.frame_info.name.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `frame_info.name.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'frame_info.name.lower', 'expression': 'frame_info.name.lower'}

- thread_analyzer.py:256 in `ThreadAnalyzer._identify_blocking_call` -> `thread_analyzer.frame_info.name.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `frame_info.name.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'frame_info.name.lower', 'expression': 'frame_info.name.lower'}

- thread_analyzer.py:277 in `ThreadAnalyzer._format_stack` -> `thread_analyzer.s.filename.split` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `s.filename.split`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 's.filename.split', 'expression': 's.filename.split'}

- thread_analyzer.py:293 in `ThreadAnalyzer.compare_snapshots` -> `thread_analyzer.snap2_threads.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `snap2_threads.get`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'snap2_threads.get', 'expression': 'snap2_threads.get'}

- thread_analyzer.py:302 in `ThreadAnalyzer.compare_snapshots` -> `thread_analyzer.stuck_threads.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `stuck_threads.append`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'stuck_threads.append', 'expression': 'stuck_threads.append'}

- thread_analyzer.py:333 in `ThreadAnalyzer.print_snapshot` -> `thread_analyzer.lead_threads.sort` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `lead_threads.sort`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'lead_threads.sort', 'expression': 'lead_threads.sort'}

- thread_analyzer.py:334 in `ThreadAnalyzer.print_snapshot` -> `thread_analyzer.bg_threads.sort` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `bg_threads.sort`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'bg_threads.sort', 'expression': 'bg_threads.sort'}

- thread_analyzer.py:335 in `ThreadAnalyzer.print_snapshot` -> `thread_analyzer.user_threads.sort` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `user_threads.sort`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'user_threads.sort', 'expression': 'user_threads.sort'}

- thread_analyzer.py:367 in `ThreadAnalyzer._print_thread` -> `thread_analyzer.severity_emoji.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `severity_emoji.get`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'severity_emoji.get', 'expression': 'severity_emoji.get'}

- thread_analyzer.py:386 in `ThreadAnalyzer._print_thread` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `frame['code'].strip`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': "frame['code'].strip"}

- thread_analyzer.py:435 in `run_standalone` -> `thread_analyzer.ThreadAnalyzer` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ThreadAnalyzer`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'ThreadAnalyzer', 'expression': 'ThreadAnalyzer'}

- thread_analyzer.py:454 in `run_standalone` -> `thread_analyzer.all_stuck.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `all_stuck.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'all_stuck.extend', 'expression': 'all_stuck.extend'}

- thread_analyzer.py:462 in `run_standalone` -> `thread_analyzer.seen.add` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `seen.add`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'seen.add', 'expression': 'seen.add'}

- thread_analyzer.py:463 in `run_standalone` -> `thread_analyzer.unique_stuck.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `unique_stuck.append`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'unique_stuck.append', 'expression': 'unique_stuck.append'}

- thread_analyzer.py:483 in `monitor_in_app` -> `thread_analyzer.ThreadAnalyzer` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ThreadAnalyzer`
  - Target info: {'type': 'unresolved', 'module_path': 'thread_analyzer', 'func_name': 'ThreadAnalyzer', 'expression': 'ThreadAnalyzer'}

- agent_manager.py:19 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:20 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:21 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:22 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:23 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:24 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:25 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:26 in `AgentConfig.__init__` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:30 in `AgentConfig.matches_trigger` -> `agent_manager.user_input.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `user_input.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'user_input.lower', 'expression': 'user_input.lower'}

- agent_manager.py:32 in `AgentConfig.matches_trigger` -> `agent_manager.trigger.lower` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `trigger.lower`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'trigger.lower', 'expression': 'trigger.lower'}

- agent_manager.py:42 in `AgentConfig.build_system_message` -> `agent_manager.parts.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parts.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'parts.append', 'expression': 'parts.append'}

- agent_manager.py:44 in `AgentConfig.build_system_message` -> `agent_manager.parts.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parts.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'parts.append', 'expression': 'parts.append'}

- agent_manager.py:47 in `AgentConfig.build_system_message` -> `agent_manager.parts.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parts.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'parts.append', 'expression': 'parts.append'}

- agent_manager.py:49 in `AgentConfig.build_system_message` -> `agent_manager.parts.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parts.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'parts.append', 'expression': 'parts.append'}

- agent_manager.py:52 in `AgentConfig.build_system_message` -> `agent_manager.parts.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parts.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'parts.append', 'expression': 'parts.append'}

- agent_manager.py:54 in `AgentConfig.build_system_message` -> `agent_manager.parts.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `parts.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'parts.append', 'expression': 'parts.append'}

- agent_manager.py:56 in `AgentConfig.build_system_message` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `'\n'.join`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': "'\\n'.join"}

- agent_manager.py:87 in `ContextManager.compress_context` -> `agent_manager.m.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `m.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'm.get', 'expression': 'm.get'}

- agent_manager.py:88 in `ContextManager.compress_context` -> `agent_manager.m.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `m.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'm.get', 'expression': 'm.get'}

- agent_manager.py:106 in `ContextManager.optimize_tool_results` -> `agent_manager.msg.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `msg.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'msg.get', 'expression': 'msg.get'}

- agent_manager.py:107 in `ContextManager.optimize_tool_results` -> `agent_manager.msg.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `msg.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'msg.get', 'expression': 'msg.get'}

- agent_manager.py:116 in `ContextManager.optimize_tool_results` -> `agent_manager.optimized.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `optimized.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'optimized.append', 'expression': 'optimized.append'}

- agent_manager.py:128 in `AgentManager.__init__` -> `agent_manager.ContextManager` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `ContextManager`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'ContextManager', 'expression': 'ContextManager'}

- agent_manager.py:135 in `AgentManager.load_agents` -> `agent_manager.agents_config_file.exists` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `agents_config_file.exists`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'agents_config_file.exists', 'expression': 'agents_config_file.exists'}

- agent_manager.py:137 in `AgentManager.load_agents` -> `yaml.safe_load` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `yaml.safe_load`
  - Target info: {'type': 'unresolved', 'module_path': 'yaml', 'func_name': 'safe_load', 'expression': 'yaml.safe_load'}

- agent_manager.py:138 in `AgentManager.load_agents` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get('agents', {}).items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': "config.get('agents', {}).items"}

- agent_manager.py:138 in `AgentManager.load_agents` -> `agent_manager.config.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `config.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'config.get', 'expression': 'config.get'}

- agent_manager.py:139 in `AgentManager.load_agents` -> `agent_manager.AgentConfig` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `AgentConfig`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'AgentConfig', 'expression': 'AgentConfig'}

- agent_manager.py:143 in `AgentManager.load_agents` -> `agent_manager.AgentConfig` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `AgentConfig`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'AgentConfig', 'expression': 'AgentConfig'}

- agent_manager.py:158 in `AgentManager.find_agents_md` -> `agent_manager.agents_file.exists` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `agents_file.exists`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'agents_file.exists', 'expression': 'agents_file.exists'}

- agent_manager.py:160 in `AgentManager.find_agents_md` -> `agent_manager.f.read` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `f.read`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'f.read', 'expression': 'f.read'}

- agent_manager.py:163 in `AgentManager.find_agents_md` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `Path('AGENTS.md').exists`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': "Path('AGENTS.md').exists"}

- agent_manager.py:165 in `AgentManager.find_agents_md` -> `agent_manager.f.read` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `f.read`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'f.read', 'expression': 'f.read'}

- agent_manager.py:172 in `AgentManager.select_agent` -> `agent_manager.user_input.startswith` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `user_input.startswith`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'user_input.startswith', 'expression': 'user_input.startswith'}

- agent_manager.py:173 in `AgentManager.select_agent` -> `agent_manager.user_input.split` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `user_input.split`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'user_input.split', 'expression': 'user_input.split'}

- agent_manager.py:179 in `AgentManager.select_agent` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.agents.items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.agents.items'}

- agent_manager.py:180 in `AgentManager.select_agent` -> `agent_manager.agent.matches_trigger` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `agent.matches_trigger`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'agent.matches_trigger', 'expression': 'agent.matches_trigger'}

- agent_manager.py:181 in `AgentManager.select_agent` -> `agent_manager.matched_agents.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `matched_agents.append`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'matched_agents.append', 'expression': 'matched_agents.append'}

- agent_manager.py:185 in `AgentManager.select_agent` -> `agent_manager.matched_agents.sort` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `matched_agents.sort`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'matched_agents.sort', 'expression': 'matched_agents.sort'}

- agent_manager.py:198 in `AgentManager.prepare_messages` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.agents.get`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.agents.get'}

- agent_manager.py:214 in `AgentManager.prepare_messages` -> `agent_manager.agent.build_system_message` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `agent.build_system_message`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'agent.build_system_message', 'expression': 'agent.build_system_message'}

- agent_manager.py:218 in `AgentManager.prepare_messages` -> `agent_manager.m.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `m.get`
  - Target info: {'type': 'unresolved', 'module_path': 'agent_manager', 'func_name': 'm.get', 'expression': 'm.get'}

- agent_manager.py:222 in `AgentManager.prepare_messages` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.context_manager.optimize_tool_results`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.context_manager.optimize_tool_results'}

- agent_manager.py:225 in `AgentManager.prepare_messages` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.context_manager.compress_context`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.context_manager.compress_context'}

- agent_manager.py:235 in `AgentManager.get_agent_tools` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.agents.get`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.agents.get'}

- agent_manager.py:245 in `AgentManager.list_agents` -> `unknown.unknown` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `self.agents.items`
  - Target info: {'type': 'unresolved', 'module_path': None, 'func_name': None, 'expression': 'self.agents.items'}

- github_tool.py:29 in `GitHubTool.check_auth` -> `github_tool.result.stdout.strip` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `result.stdout.strip`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'result.stdout.strip', 'expression': 'result.stdout.strip'}

- github_tool.py:51 in `GitHubTool.execute_command` -> `github_tool.auth_status.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `auth_status.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'auth_status.get', 'expression': 'auth_status.get'}

- github_tool.py:52 in `GitHubTool.execute_command` -> `github_tool.auth_status.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `auth_status.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'auth_status.get', 'expression': 'auth_status.get'}

- github_tool.py:57 in `GitHubTool.execute_command` -> `github_tool.cmd.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `cmd.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'cmd.extend', 'expression': 'cmd.extend'}

- github_tool.py:67 in `GitHubTool.execute_command` -> `github_tool.output.strip` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `output.strip`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'output.strip', 'expression': 'output.strip'}

- github_tool.py:79 in `GitHubTool.repo_view` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:80 in `GitHubTool.repo_view` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:81 in `GitHubTool.repo_view` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:91 in `GitHubTool.issue_list` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:92 in `GitHubTool.issue_list` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:101 in `GitHubTool.issue_view` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:102 in `GitHubTool.issue_view` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:103 in `GitHubTool.issue_view` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:112 in `GitHubTool.issue_create` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:114 in `GitHubTool.issue_create` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:123 in `GitHubTool.pr_list` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:124 in `GitHubTool.pr_list` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:133 in `GitHubTool.pr_view` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:134 in `GitHubTool.pr_view` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:135 in `GitHubTool.pr_view` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:144 in `GitHubTool.pr_create` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:146 in `GitHubTool.pr_create` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:148 in `GitHubTool.pr_create` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:157 in `GitHubTool.pr_checkout` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:166 in `GitHubTool.workflow_list` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:167 in `GitHubTool.workflow_list` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:168 in `GitHubTool.workflow_list` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:177 in `GitHubTool.workflow_run` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:186 in `GitHubTool.run_list` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:187 in `GitHubTool.run_list` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:196 in `GitHubTool.gist_create` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:198 in `GitHubTool.gist_create` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:200 in `GitHubTool.gist_create` -> `github_tool.args.append` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.append`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.append', 'expression': 'args.append'}

- github_tool.py:203 in `GitHubTool.gist_create` -> `github_tool.files.items` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `files.items`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'files.items', 'expression': 'files.items'}

- github_tool.py:204 in `GitHubTool.gist_create` -> `github_tool.args.extend` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `args.extend`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'args.extend', 'expression': 'args.extend'}

- github_tool.py:222 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:224 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:225 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:226 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:229 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:230 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:233 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:234 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:235 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:238 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:239 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:240 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:243 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:244 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:247 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:248 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:249 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:250 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:251 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:254 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:255 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:257 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:259 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:260 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:263 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:264 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:267 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:268 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

- github_tool.py:269 in `execute_github_tool` -> `github_tool.kwargs.get` (unresolved)
  - Details: Target not resolved; likely dynamic or external
  - Expression: `kwargs.get`
  - Target info: {'type': 'unresolved', 'module_path': 'github_tool', 'func_name': 'kwargs.get', 'expression': 'kwargs.get'}

... 6405 more entries omitted from summary (see JSON for full list).

## Notes

- `ok_builtin`, `ok_stdlib`, and `project_self` indicate successful resolution of language/runtime or same-class calls.
- Remaining `unresolved` entries correspond to dynamic dispatch or external dependencies requiring manual review.
- Refer to `slips_detailed.json` for the full dataset.
