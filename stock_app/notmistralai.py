from django.http import JsonResponse
from src.services.yfinance_service import StockData
import logging

logger = logging.getLogger('stock_app')

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