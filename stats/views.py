from django.shortcuts import render
from .models import Consumed_Stats, Time_Stamp
from django.utils import timezone
from datetime import timedelta
#from .forms import FilterForm

# Create your views here.
def statsHandler(request):
    # Check if we want to show the stats table
    if request.method == 'POST':

        '''
        form = forms.FilterForm(request.POST)
        choice = None
        if form.is_valid():
            choice = form.cleaned_data['select']

        if choice is 'Name':
            stats_list = Consumed_Stats.objects.order_by('-food__name')
        elif choice is 'Most Consumed':
            stats_list = Consumed_Stats.objects.order_by('-total')
        elif choice is 'Least Consumed':
            stats_list = Consumed_Stats.objects.order_by('total')
            '''

    else :
        stats_list = Consumed_Stats.objects.order_by('food__name')

    if stats_list:
        if timeCheck():
            # Need to re-get the list
            stats_list = Consumed_Stats.objects.order_by('food__name')
        context = {'stats_list': stats_list,
        'value':timezone.now(),
        'value2':timezone.now() - timedelta(days=1),
        'value3':timezone.now() - timedelta(days=2),
        'value4':timezone.now() - timedelta(days=3)}
        return render(request, 'stats/index.html', context)

    stats_list = False
    context = None
    return render(request, 'stats/index.html', context)

# Re-initializes the stats table with a parameter to distinguish the number
# of days to change
def reinitStats(day_diff):
    temp_count_array = [] # holds the values to be pushed to next day
    temp_count_array2 = [] #hold additional day
    stats_list = Consumed_Stats.objects.all()

    # Since this function is only called when a new day is detected, by default
    # all count1 values will be zeroed.
    for i in range(0, len(stats_list)):
        temp_count_array.append(stats_list[i].count1)
        stats_list[i].count1 = 0
        stats_list[i].save()

   # Now iterate through the second day values, if the difference in days is
    # equal to its respective number, keep shifting over,
    # otherwise, set those values to zero
    for i in range(0, len(stats_list)):
        if 1 >= day_diff:
            temp = stats_list[i].count2
            stats_list[i].count2 = temp_count_array[i]
            temp_count_array[i] = temp
            stats_list[i].save()
        else:
            temp_count_array2.append(stats_list[i].count2)
            stats_list[i].count2 = 0
            stats_list[i].save()

    for i in range(0, len(stats_list)):
        if 2 >= day_diff:
            temp = stats_list[i].count3
            stats_list[i].count3 = temp_count_array[i]
            temp_count_array[i] = temp
            stats_list[i].save()
        else:
            stats_list[i].count3 = 0
            stats_list[i].save()

    for i in range(0, len(stats_list)):
        if 3 >= day_diff:
            # if difference is 2 days, then it's day 2 values
            if day_diff is 2:
                stats_list[i].count4 = temp_count_array2[i]
            # else it's just what's in the first array
            else:
                stats_list[i].count4 = temp_count_array[i]
        else:
            stats_list[i].count4 = 0
        stats_list[i].total = (stats_list[i].count2 + stats_list[i].count3 +
                                stats_list[i].count4)
        stats_list[i].save()
    # Now cleanup
    cleanup()

# Cleanup fucntion remove food items in the stats table that have all counts
# equal to 0
def cleanup():
    stats_list = Consumed_Stats.objects.all()

    # Omit count1 since it's only called on new day and that day is 0
    for i in range(0, len(stats_list)):
        if (stats_list[i].count2 == 0 and stats_list[i].count3 == 0
            and stats_list[i].count4 == 0):
                stats_list[i].delete()

# Checks if the last day a food item was consumed or stat page accessed is
# different than the current day to reinitStats
def timeCheck():
    date = timezone.now()
    try:
        stat_time = Time_Stamp.objects.get(pk=1)
    except Time_Stamp.DoesNotExist:
        stat_time = Time_Stamp()
        stat_time.save()
    # return false if same day (so don't reinit) and true otherwise
    day_diff = abs((date - stat_time.time).days)
    print(day_diff)
    print(stat_time.time.day)
    if day_diff is 0:
        return
    else:
        stat_time.time = timezone.now()
        stat_time.save()
        if day_diff > 0:
            reinitStats(day_diff)
        return True
