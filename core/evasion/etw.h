#ifndef ETW_BYPASS_H
#define ETW_BYPASS_H

#ifdef _WIN32

// ETW bypass functions to disable Event Tracing for Windows
int etw_bypass_event_write(void);
int etw_bypass_trace_event(void);
int etw_restore_event_write(void);
int etw_is_patched(void);

// Patch .NET ETW functions
int etw_bypass_clr(void);

#endif // _WIN32

#endif // ETW_BYPASS_H
