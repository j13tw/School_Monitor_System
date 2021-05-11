#!bin/bash

confirm=0

while [ $confirm -eq 0 ]
do

  read -p "請輸入更新的Damain Name或IP: " update
  read -p "確認是 \"$update\" 嗎? (Y/N) " yn
  
  if [ $yn = "y" ]; then
      confirm=1
  fi
  if [ $yn = "Y" ]; then
      confirm=1
  fi

done

#echo "----- Oringin -----"
#cat /etc/supervisor/conf.d/client.conf

#echo "----- subsitution -----"
replacestr=$(awk -v update=$update -F ' ' 'NR==3 {print $1" "$2" "$3" "update" "$5}' /etc/supervisor/conf.d/client.conf)
sed -i "3c $replacestr" /etc/supervisor/conf.d/client.conf

echo "----- Done -----"
cat /etc/supervisor/conf.d/client.conf

echo  "----- restarting supervisor -----"
supervisorctl reload
supervisorctl restart all
