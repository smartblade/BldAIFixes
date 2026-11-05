#ifndef CONSOLE_H

#define CONSOLE_H

class B_MessageChannel;

/* Blade.exe calls these functions through import thunks: not dllimport */
extern "C"
{

B_MessageChannel *CreateConsole(
    HWND parentWindow, const char *name, int x, int y, int width, int height,
    int isChild);
void DestroyConsole(void *console);

}

#endif /* CONSOLE_H */
