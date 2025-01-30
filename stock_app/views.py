from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET
import plotly.express as px
from .forms import StockForm
from src.services.yfinance_service import StockData, StockDataError
from .mistral_ai import MistralAIClient  # Import the utility class
import logging
import asyncio

logger = logging.getLogger('stock_app')

# Initialize Mistral AI client
mistral_client = MistralAIClient()


def stock_view(request):
    """
    Handle the stock visualization form and generate Plotly graphs.
    """
    graph_html = None
    form = StockForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        ticker = form.cleaned_data['ticker']
        period = form.cleaned_data['period']
        interval = form.cleaned_data['interval']

        logger.info(f"Processing request for {ticker} with {period} period and {interval} interval")

        try:
            stock = StockData(ticker, period, interval)
            df = stock.get_historical_data()

            fig = px.line(
                df,
                x=df.index,
                y='Close',
                title=f'{ticker.upper()} Stock Price',
                template='plotly_white'
            )

            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                hovermode='x unified'
            )

            graph_html = fig.to_html(full_html=False, config={'displayModeBar': True})

        except StockDataError as e:
            logger.error(f"Stock data error: {str(e)}")
            graph_html = f"<div class='alert alert-danger'>{str(e)}</div>"

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            graph_html = "<div class='alert alert-danger'>An unexpected error occurred</div>"

    context = {
        'form': form,
        'graph_html': graph_html,
    }

    return render(request, 'stock_app/stock.html', context)


@require_GET
def get_intervals(request):
    """
    Handle AJAX GET requests to fetch available intervals based on the selected period.
    Expects a 'period' parameter in the query string.
    """
    period = request.GET.get('period')
    if not period:
        logger.warning("No 'period' parameter provided in get_intervals request.")
        return JsonResponse({'error': "Missing 'period' parameter."}, status=400)
    
    try:
        # Fetch intervals based on the period
        intervals = StockData.get_available_intervals(period)  # This should return a list of interval strings
        
        logger.debug(f"Fetched intervals for period '{period}': {intervals}")
        return JsonResponse({'intervals': intervals}, status=200)
    
    except Exception as e:
        logger.error(f"Error fetching intervals for period '{period}': {e}")
        return JsonResponse({'error': 'Failed to fetch intervals.'}, status=500)


@csrf_protect
async def chat_with_ai(request):
    """
    Handle AJAX POST requests to chat with Mistral AI asynchronously.
    Expects 'message', 'ticker', 'period', and 'interval' in POST data.
    """
    if request.method == 'POST':
        user_message = request.POST.get('message')
        selected_ticker = request.POST.get('ticker')
        period = request.POST.get('period')
        interval = request.POST.get('interval')

        if not user_message or not selected_ticker or not period or not interval:
            return JsonResponse({'error': 'Invalid data provided.'}, status=400)

        try:
            # Use asyncio to run the synchronous get_response method in a thread
            ai_response = await asyncio.to_thread(
                mistral_client.get_response, user_message, selected_ticker, period, interval
            )
            return JsonResponse({'response': ai_response})

        except Exception as e:
            logger.error(f"Error in chat_with_ai view: {e}")
            return JsonResponse({'error': 'Failed to process your request.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)