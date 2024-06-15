# Stock Market Assist Dashboard (under development, phase 1 completed)

This Streamlit app provides a comprehensive dashboard for monitoring stocks, including equities and futures and options (F&O) instruments. It fetches real-time stock data and news from multiple sources, allowing users to stay updated on the latest market developments.

## Features

- **Stock Listing**: View a list of all equity and F&O stocks with their current prices and other relevant information.
- **News Feed**: Stay informed with the latest news articles from various sources related to the stock market.
- **Stock Details**: Get detailed information about a specific stock, including its price history, technical indicators, and relevant news articles.

## Getting Started

1. Clone the repository:

  ```bash
  git clone https://github.com/your-username/stock-market-dashboard.git
  cd stock-market-dashboard
  ```

2. Install the required dependencies:

  ```bash
  pip install -r requirements.txt
  ```

3. Duplicate the `.env.example` file and rename it to `.env`. Then, fill in the required API keys for the data sources you want to use.

4. Run the application:

  ```bash
  ./run.sh
  ```

  This script will start the Streamlit app and open it in your default web browser.

## Configuration

The application uses the following environment variables for configuration. Make sure to set them in the `.env` file:

- `SUPABASE_URL`: API key for fetching stock data.
- `SUPABASE_KEY`: API key for fetching news articles.
- `MC_AUTH_TOKEN`: API key for any other data source you want to use.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
