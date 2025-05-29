#!/bin/bash

#
#  Cours "Sémantique et Application à la Vérification de programmes"
#
#  Ecole normale supérieure, Paris, France / CNRS / INRIA
#

shopt -s lastpipe
RED="\e[91m"
GREEN="\e[92m"
BOLD="\e[1m"
RESET="\e[0m"
BLUE="\e[94m"
fill="                                                     "
# Default solver path. You can change it if you need
analyzer_path=$1
analyzer=$analyzer_path/bin/analyzer
options=$analyzer_path/options.txt

result_folder="results"
index_html="${result_folder}/index.html"

nb_test=0
timeout=0
failure=0
completness=0
soundness=0

# max time allowed
max_time="5s"

all_opts="$2"
if [ "$all_opts" != "" ]; then
  echo "Launching code with extra options: '${all_opts}'"
fi

# Pattern for failure in log
patt_assert="line [0-9]*: Assertion failure"
# Pattern for expêctyed failure in file
patt_ko="assert.*//@KO"

create_file() {
  file=$1
  filename=$(basename $file)
  file_html="${result_folder}/${filename}.html"
  if [[ ! -e "$file_html" ]]
  then
    cat "scripts/header.html" > $file_html
    sed -i "s@TITLE@${filename}@" $file_html
    echo "<h1>${filename}</h1>" >> $file_html
    echo "<div class=\"c\">" >> $file_html
    cat $file >> $file_html
    echo "</div>" >> $file_html
    file_svg=$(basename ${file})".svg"
    echo "<img src=\"./${file_svg}\" alt=\"graph\">" >> $file_html
  fi
}

end_file() {
  # After the analysis the cfg.dot should correspond to the current test
  dot -Tsvg cfg.dot -o ${result_folder}/${filename}.svg
  cat "scripts/footer.html" >> $file_html
}

get_nth_line() {
  line=$1
  file=$2
  sed "${line}q;d" $file
}

treat_file() {
  file=$1
  log=$2
  expected_folder=$3
  need_new_line=true
  sound_loc=0
  compl_loc=0
  col_sound="green"
  col_compl="green"

  # first, we compute the expected failures
  if [[ "$expected_folder" == "" ]]
  then
    nb_expected=$(grep -n "${patt_ko}" $file| wc -l)
    expected=$(grep -n "${patt_ko}" $file | grep -o "^[0-9]*")
  else
    file_folder=$(dirname $file)
    file=$(basename $file)
    res="${file_folder}/${expected_folder}/${file}.log"
    nb_expected=$(grep "${patt_assert}" $res | wc -l)
    expected=$(grep "${patt_assert}" $res | grep -o "line [0-9]*" | grep -o "[0-9]*")
  fi
  # then, we compute the failed assertions
  nb_failures=$(grep "${patt_assert}" $log| wc -l)
  failures=$(grep "${patt_assert}" $log | grep -o "line [0-9]*" | grep -o "[0-9]*")

  echo "<p><span style=\"color: blue;\">Expected:</span> ${expected} </p>" >> $file_html
  echo "<p><span style=\"color: blue;\">Failures:</span> ${failures} </p>" >> $file_html

  # echo -e "\nnb_expected: ${nb_expected}"
  # echo -e "expected:\n--\n${expected}\n--"
  # echo -e "nb_failures: ${nb_failures}"
  # echo -e "failures:\n--\n${failures}\n--"

  # Soundness part: for line number in expected,
  # we search for it in failures
  for nb in `seq 1 $nb_expected`;
  do
    cmd="echo \"${expected}\" | head -${nb} | tail -1"
    line_nb=$(eval "${cmd}")
    echo "${failures}" | grep -q "^${line_nb}$"
    found=$?
    if [[ $found -ne 0 ]]
    then
      line=$(get_nth_line $line_nb $file)
      col_sound="red"
		  soundness=$((soundness+1))
		  sound_loc=$((sound_loc+1))
      if [ "$need_new_line" = true ]
      then
        echo -e "\n${BOLD}${RED} SOUNDNESS ERRORS${RESET}"
        need_new_line=false
      else
        echo -e "${BOLD}${RED} SOUNDNESS ERRORS${RESET}"
      fi
      echo -e "${RED}missing fail assertions:${RESET}${line}"
      echo "<p>${line_nb}<span style=\"color: red;\">${line}</span></p>" >> $file_html
    fi
  done

  # Completness part: for each line number in failures,
  # we search for it in expected
  for nb in `seq 1 $nb_failures`;
  do
    cmd="echo \"${failures}\" | head -${nb} | tail -1"
    line_nb=$(eval "${cmd}")
    echo "${expected}" | grep -q "^${line_nb}$"
    found=$?
    if [[ $found -ne 0 ]]
    then
		  completness=$((completness+1))
		  compl_loc=$((compl_loc+1))
      col_compl="blue"
      line=$(grep "${patt_assert}" $log | head -${nb} | tail -1)
      if [ "$need_new_line" = true ]
      then
        echo -e "\n${BOLD}${BLUE} COMPLETNESS ERROR${RESET}"
        need_new_line=false
      else
        echo -e "${BOLD}${BLUE} COMPLETNESS ERROR${RESET}"
      fi
      echo -e "${BLUE}unexpected fail assertions:${RESET} ${line}"
      echo "<p><span style=\"color: blue;\">${line}</span></p>" >> $file_html
    fi
  done
  echo "<h3>LOG</h3>" >> $file_html
  echo "<pre>" >> $file_html
  cat $log >> $file_html
  echo "</pre>" >> $file_html
  if [ "$need_new_line" = false ]
  then
    echo -e ""
  fi
  echo -n "<a href=\"../${log}\" target=\"_parent\">" >> $index_html
  echo -n "<span style=\"color: ${col_sound};\">${sound_loc}</span>, " >> $index_html
  echo -n "<span style=\"color: ${col_compl};\">${compl_loc}</span>" >> $index_html
  echo "</a>" >> $index_html
}

treat_examples() {
  folder="examples/${1}"
  bench_name=$2
  options="$3 $all_opts"         # analyzer CLI options
  expected_folder=$4             # subfolder containing expected result
  bench_regexp="${folder}/*.c"
	nb_file=$(find $folder -iname "*.c" | wc -l)
  nb_test=$(( nb_test + nb_file ))
	if [[ $nb_file -eq 0 ]]
	then
    echo "bench ${bench_name}: No files found (${bench_regexp})"
    return
	fi
  echo "<tr><th colspan=\"100\" class=\"bench\">${bench_name} ${options}</th></tr>" >> $index_html
	for file in $(find "${folder}" -iname "*.c" | sort)
	do
    filename=$(basename $file)
    create_file $file
    echo "<tr><td><a href=\"${filename}.html\"><pre>${filename}</pre></a></td>" >> $index_html
    echo "<td>" >> $index_html
		solved=$(($solved+1))
		echo -ne "\r\t$file $option $fill"
    opt_replaced=$(echo "${options}" | sed "s/ /_/g")
		log="${result_folder}/${filename}.${opt_replaced}.txt"
    echo "<h2><a href=\"../${log}\">${analyzer} ${options}</a></h2>" >> $file_html
	 	timeout $max_time $analyzer $options $file > $log 2>&1
		out=$?
		if [[ $out -eq 127 ]]
		then
		  timeout=$((timeout+1))
      echo "<a href=\"../${log}\"><span style=\"color: red;\">TO</span></a>" >> $index_html
      echo "<span style=\"color: red;\">TO</span>" >> $file_html
		  echo -e "\n  ${BOLD}${RED}TO ${RESET}\n"
      echo "<h3>LOG</h3>" >> $file_html
      echo "<pre>" >> $file_html
      cat $log >> $file_html
      echo "</pre>" >> $file_html
		elif [[ $out -ne 0 ]]
		then
		  failure=$((failure+1))
      echo "<a href=\"../${log}\"><span style=\"color: red;\">FAIL</span></a>" >> $index_html
      echo "<span style=\"color: red;\">FAIL</span>" >> $file_html
		  echo -e "\n  ${BOLD}${RED}FAILED ($out) ${RESET}\n"
      echo "<h3>LOG</h3>" >> $file_html
      echo "<pre>" >> $file_html
      cat $log >> $file_html
      echo "</pre>" >> $file_html
    else
      treat_file $file $log $expected_folder
    fi
    echo "</td>" >> $index_html
    echo "</tr>" >> $index_html
    end_file $file
	done
}

print_end() {
  echo " "
  echo -e "  test:\t${nb_test} (files: ${total})"
  if [[ $timeout != 0 ]]
  then
    echo -e "  ${BOLD}Timeout${RED}\tKO (${timeout}) ${RESET}"
  fi
  if [[ $failure != 0 ]]
  then
    echo -e "  ${BOLD}Failure${RED}\tKO (${failure}) ${RESET}"
  fi
  if [[ $soundness != 0 ]]
  then
    echo -e "  ${BOLD}Soudness${RED}\tKO (${soundness}) ${RESET}"
  else
	  echo -e "  ${BOLD}Soudness${GREEN}\tOK ${RESET}"
  fi
  if [[ $completness != 0 ]]
  then
    echo -e "  ${BOLD}Completness${RED}\tKO (${completness}) ${RESET}"
  else
	  echo -e "  ${BOLD}Completness${GREEN}\tOK ${RESET}"
  fi
  echo -e "${BOLD}${BLUE}Results written in${RESET}: ${index_html}"
}

mkdir ${result_folder}
cat "scripts/header_main.html"                     > $index_html
echo "<h1>Overview</h1>"                          >> $index_html
echo "<table>"                                    >> $index_html
total=$(find $bench -iname "*.c" | wc -l)
solved=0
treat_examples "bool" "Boolean operations" "--domain constants" ""
treat_examples "bool" "Boolean operations" "--domain interval" ""
treat_examples "constant" "Constants operations" "--domain constants" ""
treat_examples "constant_loop" "Constants loops" "--domain constants" ""
treat_examples "constant" "Constants operations (I)" "--domain interval" ""
treat_examples "interval" "Interval operations" "--domain interval" ""
treat_examples "constant_loop" "Constants loops (I)" "--domain interval" ""
treat_examples "interval_loop" "Interval loops" "--domain interval" ""
echo "</table>"                                   >> $index_html
echo "</body>"                                    >> $index_html
echo "</html>"                                    >> $index_html
print_end
