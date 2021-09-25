# Asset Tycoon Crypto Bot

## Installation

- download repository (it is recommended to use only stable **[releases](https://github.com/GitHub-Leon/Trading_Bot_Binance/releases)** as a safety measure).

### Windows

- install python 3.7

**setup trading-bot**
```
setup.bat PATH_TO_PYTHON3.7
```

### Linux

```
bash setup.sh
bash start.sh
```
  
---------------

In order to be able to use the bot correctly, you have to deposit the credentials.

You first need permission to trade with leverage coins.

## Usage

### Execute

#### Windows

```
start.bat
```

#### Linux

```
bash start.sh
```

### Commands

- **start** (starts the bot)
- **Strg + C** (stops the bot)
- **exit** (exit application)
- **settings** (opens config file to edit configuration)
- **creds** (opens creds file to edit)
- **plot** (plots the portfolio value)

### Credentials File: `creds.yml`

    prod:  
      access_key: replace_me  
      secret_key: replace_me  
      
    discord:  
      DISCORD_WEBHOOK_TRADES: https://discord.com/api/webhooks/XXX/YYYYY  
      DISCORD_WEBHOOK_BALANCE: https://discord.com/api/webhooks/XXX/YYYYY

**[Binance Creds Link](https://www.binance.com/en-IN/support/faq/360002502072)**

**[Discord Webhooks Tutorial](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)**

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

      PAY_FEE_WITH_BNB: True

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

- script_options [**These options apply to how the script will operate**]
    - TEST_MODE [**Switch between testnet and mainnet**]
    - LOG_TRADES [**Logs each trade in a log file**]
    - MSG_DISCORD [**Used to push alerts, messages etc to a discord channel**]
    - AMERICAN_USER [**Used for binance.us**]
    - PRINT_CONFIG_AT_START [**Prints current configs at start**]
    - DEBUG [**Debug mode gets more alerts**]
- trading_options [**These options apply to the trading methods the script executes**]
    - PAIR_WITH [**select what to pair the coins to and pull all coins paired with PAIR_WITH**]
    - SELL_WHEN_BEARISH [**sell all currently owned coins when pausebot_standard stops bot because of bearish movement**]
    - SELL_ALL_AT_END [**sell all currently held coins at program exit**]
    - TRADING_FEE [**Fees in percent**]
    - PAY_FEE_WITH_BNB [**Auto buy feature for BNB to cover fees**]
    - QUANTITY [**Total amount per trade**]
    - CUSTOM_LIST [**Use custom tickers.txt list for filtering pairs**]
    - FIATS [**List of pairs to exclude (by default we're excluding the most popular fiat/leverage pairs)**]
    - USE_LEVERAGE [**Enables the use of leveraged coins (comment out DOWN and UP at option FIATS)**]
    - USE_LIMIT_ORDERS [**True if limit orders should be used instead of market orders**]
    - MAX_COINS [**Maximum number of different coins to hold**]
    - TIME_DIFFERENCE [**the amount of time in MINUTES to calculate the difference from the current price**]
    - RECHECK_INTERVAL [**Number of times to check for TP/SL during each TIME_DIFFERENCE Minimum 1**]
    - STOP_LOSS [**define in % when to sell a coin that's not making a profit**]
    - TAKE_PROFIT [**define in % when to take profit on a profitable coin**]
- strategy_options [**Options that apply to specific strategies**]
    - volatility
        - USE_DEFAULT_STRATEGY [**whether to use default settings or not; default is True**]
        - CHANGE_IN_PRICE [**the difference in % between the first and second checks for the price**]
    - trailing_sl [**when hit TAKE_PROFIT, move STOP_LOSS to TRAILING_STOP_LOSS percentage points below TAKE_PROFIT hence locking in profit | when hit TAKE_PROFIT, move TAKE_PROFIT up by TRAILING_TAKE_PROFIT percentage points**]
        - USE_TRAILING_STOP_LOSS [**whether to use trailing stop loss or not; default is True**]
        - TRAILING_STOP_LOSS
        - TRAILING_TAKE_PROFIT
    - trading_view
        - SIGNALLING_MODULES [**List of strategies to use. [Modules](https://github.com/GitHub-Leon/Trading_Bot_Binance/blob/master/src/threads/strategy_threads/README.md)**]



## Recommended Environments

 - Windows 10
 - Raspbian
 - Ubuntu

**© Asset Tycoon 2021**
