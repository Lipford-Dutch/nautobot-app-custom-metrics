# V1 First-Batch Metrics

The v1 first batch implements the ROI efficiency metrics from Section 2.1 of the metrics definition guide. These metrics focus on measurable outcomes from Nautobot-backed automation and are intentionally narrow enough to validate end to end before expanding into cost, business-impact, user-activity, plugin, and system-performance categories.

| Metric | Key | Unit | Formula | Sample context |
| --- | --- | --- | --- | --- |
| Time Saved per Automated Task | `time_saved_per_automated_task` | Hours | `Time_Manual - Time_Automated` | Task name, manual hours, automated hours |
| Reduction in Manual Error Rates | `manual_error_rate_reduction` | Percent | `(Error_Rate_Manual - Error_Rate_Automated) / Error_Rate_Manual * 100` | Task name, manual error rate, automated error rate |
| Increased Task Throughput | `increased_task_throughput` | Percent | `(Tasks_Completed_Automated - Tasks_Completed_Manual) / Tasks_Completed_Manual * 100` | Task name, manual count, automated count, period |
| Automation Adoption Rate | `automation_adoption_rate` | Percent | `(Number_of_Tasks_Automated / Total_Potential_Tasks_for_Automation) * 100` | Automated tasks, total target tasks, team |

## Implementation Notes

- The sample-data job creates one daily observation per metric for the requested sample window.
- The job is idempotent by metric definition, timestamp, and source.
- Adoption and manual error-rate reduction are bounded percentages from `0` to `100`.
- Throughput improvement is a percent-change metric and can exceed `100`.
- All four metrics are available in the dashboard and summary API after the sample-data job runs.
