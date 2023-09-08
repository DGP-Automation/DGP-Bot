# Docker Image Settings
imageName=dgp-github-bot
containerName=DGP-GitHub-Bot
imageVersion=1.9
externalPort=3524
internalPort=8000

oldContainer=`docker ps -a| grep ${containerName} | head -1|awk '{print $1}' `
echo Delete old container...
docker rm  $oldContainer -f
echo Delete success

docker build -f Dockerfile -t $imageName:$imageVersion .
docker run -d -itp $externalPort:$internalPort \
    -v $(pwd)/.env:/app/.env \
    --restart=always \
    --name="$containerName" \
    $imageName:$imageVersion