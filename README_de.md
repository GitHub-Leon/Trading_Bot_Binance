# Asset Tycoon Crypto Bot

## Installation

- herunterladen des Repositories (aus Sicherheit ist es empfohlen nur stabile **[Releases](https://github.com/GitHub-Leon/Trading_Bot_Binance/releases)** zu nutzen).
- installieren von **[python](https://www.python.org/downloads/)**. 
- führe **setup.bat** aus [[linux](https://www.linux.org/threads/running-windows-batch-files-on-linux.11205/)]
- doppelklick auf **trading_bot.py**

Wenn du den Bot richtig nutzen willst, dann musst du die Credentials im cred File angeben.

## Benutzung

### Kommandos

- **start** (startet den Bot)
- **Strg + C** (stoppt den Bot)
- **exit** (schließt das Programm)
- **settings** (öffnet die Konfigurationen)
- **creds** (öffnet die Credentials)

### Credentials File: `creds.yml`

    prod:  
      access_key: replace_me  
      secret_key: replace_me  
      
    discord:  
      DISCORD_WEBHOOK_TRADES: https://discord.com/api/webhooks/XXX/YYYYY  
      DISCORD_WEBHOOK_BALANCE: https://discord.com/api/webhooks/XXX/YYYYY

**[Binance Credentials Link](https://www.binance.com/de/support/faq/360002502072)**

**[Discord Webhooks Tutorial](https://support.discord.com/hc/de/articles/228383668-Einleitung-in-Webhooks)**

### Config File: `config.yml`

    script_options:
      TEST_MODE: True
      LOG_TRADES: True
      MSG_DISCORD: False
      AMERICAN_USER: False
      PRINT_CONFIG_AT_START: False
      DEBUG: False
    
    trading_options:
      PAIR_WITH: USDT
    
      SELL_WHEN_BEARISH: False
    
      SELL_ALL_AT_END: True
   
      TRADING_FEE: 0.075
    
      QUANTITY: 150
    
      CUSTOM_LIST: True
      
      FIATS:
        - EURUSDT
        - GBPUSDT
        - JPYUSDT
        - USDUSDT
        - DOWN  # comment out if USE_LEVERAGE == True
        - UP  # comment out if USE_LEVERAGE == True
    
      USE_LEVERAGE: False
    
      USE_LIMIT_ORDERS: True
    
      MAX_COINS: 20
    
      TIME_DIFFERENCE: 1
    
      RECHECK_INTERVAL: 6
    
      STOP_LOSS: 1
    
      TAKE_PROFIT: 0.2
    
    strategy_options:
      volatility:
        USE_DEFAULT_STRATEGY: True
    
        CHANGE_IN_PRICE: 1
    
      trailing_sl:
        USE_TRAILING_STOP_LOSS: True
    
        TRAILING_STOP_LOSS: 0.01
        
        TRAILING_TAKE_PROFIT: 0.01
    
      trading_view:
        SIGNALLING_MODULES:
          - signal_standard
          - pausebot_standard

- script_options [**Diese Optionen tragen zur Funktionsweise des Bots bei**]
    - TEST_MODE [**Wechselt zwischen dem Testnet und dem Mainnet**]
    - LOG_TRADES [**Dokumentiert alle Trades in einem log File mit**]
    - MSG_DISCORD [**Kann festlegen ob Benachrichtigungen, Nachrichten etc in einen Discord Channel gepostet werden sollen.**]
    - AMERICAN_USER [**Wird für binance.us Unterstützung benutzt**]
    - PRINT_CONFIG_AT_START [**Schreibt die aktuell genutzten Konfigurationen vor dem Start des Bots auf die Konsole**]
    - DEBUG [**Debug Modus bekommt mehr Nachrichten**]
- trading_options [**Allgemeine Trading Strategien**]
    - PAIR_WITH [Gibt an, mit welcher Währung/Coin gepaart werden soll. Aufgrunddessen ergeben sich auch die Paarpreise]
    - SELL_WHEN_BEARISH [Verkaufe alle derzeitigen Coins, wenn pausebot_standard den bot aufgrund eines bearishen movement stoppt]
    - SELL_ALL_AT_END [Verkaufe alle Coins, die derzeit gekauft sind, bei beenden des Programms]
    - TRADING_FEE [Gebühren in Prozent]
    - QUANTITY [Maximaler Betrag pro Trade]
    - CUSTOM_LIST [Benutze ein eigene txt Datei um Paare zu filtern]
    - FIATS [Liste der Paare welche exkludiert werden sollten (standardmäßig werden die bekanntesten Fiat/Leverage Paare exkludiert)]
    - USE_LEVERAGE [Aktiviert die Benützung von Leverage Tokens (kommentiere DOWN und UP aus -> FIATS)]
    - USE_LIMIT_ORDERS ['True', falls limit orders anstatt market orders benutzt werden sollen]
    - MAX_COINS [Maximale Anzahl an verschienen Coins, die gleichzeitig gehalten werden können]
    - TIME_DIFFERENCE [Die Zeit in MINUTEN zwischen der Berechnung zur Preisdifferenz]
    - RECHECK_INTERVAL [Wie oft TP/SL während TIME_DIFFERENCE geprüft werden soll. Minimum 1]
    - STOP_LOSS [Ab welcher Preisänderung ins negative, seit Kauf, der Coin verkauft werden soll]
    - TAKE_PROFIT [Ab welcher Preisänderung ins positive, seit Kauf, der Coin verkauft werden soll]
- strategy_options [Einstellungen die sich auf bestimmte Strategien beziehen]
    - volatility
        - USE_DEFAULT_STRATEGY [Einstellung zum Aktivieren/Deaktivieren der Standard Ausbruch-Strategie]
        - CHANGE_IN_PRICE [Der Unterschied, der zwischen den zwei Überprüfungen erreicht werden muss, um ein Kaufsignal zu geben]
    - trailing_sl [Sobald der TAKE_PROFIT erreicht wird, wird der STOP_LOSS und TAKE_PROFIT um TRAILING_STOP_LOSS und TRAILING_TAKE_PROFIT Prozentpunkte nach oben verschoben. Dies verhindert zu frühes Profit taken.]
        - USE_TRAILING_STOP_LOSS [Einstellung zum Aktivieren/Deaktivieren der trailing_stop_loss Funktion; Standartmäßig auf 'True']
        - TRAILING_STOP_LOSS
        - TRAILING_TAKE_PROFIT
    - trading_view
        - SIGNALLING_MODULES [Eine Liste der verfügbaren Strategien. [Modules](https://github.com/GitHub-Leon/Trading_Bot_Binance/src/strategies/README.md)]



## Empfohlene Umgebungungen 

 - Windows 10
 - Raspbian
 - Ubuntu

**© Asset Tycoon 2021**
