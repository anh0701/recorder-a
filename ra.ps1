# install ffmpeg

Set-ExecutionPolicy RemoteSigned -scope CurrentUser
iwr -useb get.scoop.sh | iex

scoop bucket add main
scoop install main/ffmpeg

# 
