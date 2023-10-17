# Image Settings
imageName=dgp-github-bot
imageVersion=1.11

docker build --no-cache -f Dockerfile -t $imageName:$imageVersion --target runtime .