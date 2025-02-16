zerodir=$(pwd)
file=task.txt
for i in $(seq 1 $(wc -l < "$file")); do
    j=$(sed -n "${i}p" "$file")
    echo "Line $i: $j"
    rm -rf ./case1_calcs/$i/ || true
    cp -r ./case1 ./case1_calcs/$i/
    cd ./case1_calcs/$i
    ./Allclean && ./Allprep $j && pvpython script.py
    cd $zerodir
done