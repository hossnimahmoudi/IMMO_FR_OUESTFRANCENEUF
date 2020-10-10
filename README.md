#######################
# FR_OUESTFRANCE_NEUF  ( less than an hour, expecting around 830 items) 
#######################
#in b.metge folder
source /home/b.metge/venv/FR_OUESTFRANCE_NEUF/bin/activate
cd /home/b.metge/Projects/FR_OUESTFRANCE_NEUF/
nohup scrapy crawl myspider &
# check if everything is running OK :
tail -f ouestfranceneuf.log
# result will be in 
myspider_products.json
myspider_products.csv
# Logs are in 
ouestfranceneuf.log

# If any problems, you can find some results of previvous crawl in the folder named ".scrapy/FR_OUESTFRANCENEUF"
