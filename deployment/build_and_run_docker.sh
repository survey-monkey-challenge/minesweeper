PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $PWD/..
docker build -f deployment/Dockerfile -t minesweeper .
docker run -it -p 80:80 minesweeper
