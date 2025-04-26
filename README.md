# Amazon Price Comparison Tool

A web application that compares product prices across different Amazon domains.

## Features

- Search products by name or product ID (ASIN)
- Compare prices across multiple Amazon domains
- View product previews and URLs
- Real-time price updates

## Deployment

This project is deployed using GitHub Pages. The deployment is automated using GitHub Actions.

### Manual Deployment

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/amazon_finder.git
   cd amazon_finder
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   uvicorn src.main:app --reload
   ```

4. Open your browser and navigate to `http://localhost:8000`

### GitHub Pages Deployment

The site is automatically deployed to GitHub Pages when changes are pushed to the main branch. The deployment process:

1. Builds the static files
2. Deploys them to the `gh-pages` branch
3. Makes the site available at `https://yourusername.github.io/amazon_finder`

## Configuration

To configure the application:

1. Update the `countries` dictionary in `src/amazon_price_comparison.py` to add or remove Amazon domains
2. Modify the timeout settings in the `AmazonPriceComparer` class if needed
3. Update the UI by modifying the files in `src/static` and `src/templates`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
