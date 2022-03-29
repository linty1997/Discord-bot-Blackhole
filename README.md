# Discord Bot : black hole
 協助各 NFT 項目收集錢包地址的機器人.  
 文檔 : [Docs](https://docs.wormhole.wiserver.tw/black-hole-bot/introduce "Docs")  
 邀請連結 : [Click me to invite the bot](https://discord.com/api/oauth2/authorize?client_id=958304389561462834&permissions=2147847168&scope=bot%20applications.commands "Click me to invite the bot")
 
![1648569558302](https://user-images.githubusercontent.com/40823034/160655387-ac94192d-c5bd-4490-ab55-fd35730ba750.gif =300x300)

------------

## 特色
- 簡單設置, 無複雜指令交互
- 邀請後即可使用, 無須安裝
- 永久免費, 無任何月費制度
- 完整開源以供審查

------------

## 功能
- 設置並發送一個按鈕至指定頻道, 以收集地址.
- 按鈕可完全自訂義, 包括樣式, 按鈕標籤, emoji...
- 可隨時開啟或關閉按鈕交互/編輯.
- 將蒐集的地址匯出至指定格式, 支援: Excel, csv, txt, json.

------------


## 相關指令
> 以下指令僅限 MOD 使用 (需有管理訊息權限)
- /add-button 設置並添加一個按鈕.
- /del-button 刪除按鈕並清除已收集的資料.
- /open-button 開啟按鈕交互, 允許被點擊.
- /close-button 關閉按鈕交互, 禁止被點擊.
- /open-edit 允許用戶多次提交以更改地址.
- /close-edit 禁止用戶重複提交.
- /edit_max_submit 設置提交最大上限, 達上限則無法繼續提交.(0 為不限)
- /check_user_data 獲取指定用戶已提交的地址.

> 以下指令所有人皆可使用
- /check_data 獲取已提交的地址.

------------


## 代碼相關
本機器人使用 `python` 撰寫, 運行於 `python-3.10` 並使用 `pycord` 套件調用 `Discord API` 達成各種操作.  
可於 `cmds` 資料夾中查看主要功能代碼.

------------


## 聲明
本人無法保證機器人能永久運作下去, 可能因 套件 或 Discord 官方的政策修改而在未來某一天無法使用.  
如果在使用上發現任何 Bug 歡迎發 Issue.
