# Python 7zip ReCompress!
Required software
+ [Python 3](https://www.python.org/downloads)
+ [7zip](https://www.7-zip.org/download.html)
## Usage
1. Install required software
	> Ubuntu : `$ sudo apt-get install -y python3 p7zip*`  
	> Windows : download and install [7zip](https://www.7-zip.org/download.html) and [Python](https://www.python.org/downloads)
	
2. Download [here](https://raw.githubusercontent.com/Wireless4024/Py7zRecompress/master/py7zRecompress.py)  
	##### via command line  
	> Ubuntu : `$ wget https://raw.githubusercontent.com/Wireless4024/Py7zRecompress/master/py7zRecompress.py`  
	> Windows : `> curl -o py7zRecompress.py https://raw.githubusercontent.com/Wireless4024/Py7zRecompress/master/py7zRecompress.py`

3. Run! `$ python py7zRecompress.py <Folder> [Thread] [Deep] [Extension Sensitive] [Dictionary size] [7z]` 
	> `Folder` : (`directory`) Folder that contains compress-able files `[7z, xz, zip, jar, rar]`  
	> `Thread` : (`int`) Working thread count (required more memory) (default : `1`)  
	> `Deep`   : (`int`) How deep to re-compress (useful when you have zip inside zip again and again) (default : `2`)  
	> `Extension Sensitive` : (`yes`|`no`) use compress algorithm same with file extension (default : `no`)  
	> `Dictionary size`     : (`int{k|m|g}`) size of dictionary used by `7z` and `xz` (default : `96m`)  
	> `7z`     : path to 7z executable (default : "`7z.exe`|`7z`")  
	
	### Example : 
	##### you can leave it alone like so
	>`> python py7zRecompress.py "C:\Users\Administrator\Downloads"`  
	##### or you can do this
	>`> python py7zRecompress.py "C:\Users\Administrator\Downloads" 2 5 no 128m`
	>> it will scan compress-able files inside `C:\Users\Administrator\Downloads` then re-compress itself and compress-able file inside of it with in 2 threads

	### *Note
	`Deep` parameter will very very slow if file/folder contains lots of file  
	> _**it's will work even it's not efficient**_
