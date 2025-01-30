from django.shortcuts import render
from django.http import JsonResponse
import plotly.express as px
from .forms import StockForm
from src.services.yfinance_service import StockData, StockDataError
import logging

logger = logging.getLogger('stock_app')

def stock_view(request):
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

def get_intervals(request):
    """
    Handle AJAX request to fetch intervals based on selected period.
    """
    period = request.GET.get('period')
    if period:
        intervals = StockData.get_available_intervals(period)
        logger.info(f"Fetched intervals for period '{period}': {intervals}")
        return JsonResponse({'intervals': intervals})
    logger.warning("No period provided in request to get_intervals")
    return JsonResponse({'intervals': []})