# 

## flow

```sh
ModeBar
   │
   ├── FREE
   ├── 16:9
   ├── 9:16
   ├── 1:1
   ├── 1 Screen
   └── All Screen
          │
          ▼
       Overlay
          │
          ▼
   SelectionController
          │
       ┌──┴───┐
       │      │
     Move   Resize
       │      │
       └──┬───┘
          ▼
   SelectionToolbar
     │           │
 Cancel       Start
                │
                ▼
          Recorder.start()
```