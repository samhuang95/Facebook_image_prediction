# Facebook_image_prediction<br>

## ▍功能說明<br>
使用 Facebook API，獲取粉絲專頁數據、訓練照片，最後進行預測成效<br>
目前經歷實際測試後，成功預測約莫 84%<br>
<img decoding="async" src="https://i.imgur.com/2ijcIlb.png" width="50%">
## ▍程式介紹<br>
一、FB API 串接<br>
get_fanpage_access_token.py<br>
get_facebook_data.py<br>

二、數據儲存進資料庫<br>
connect_to_db.py<br>
update_db.py<br>

三、訓練 Inception V3 模型<br>
FB_imagetest.ipynb<br>
vaild_image.py<br>

四、成效驗證<br>
image_predict.py<br>


