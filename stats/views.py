from django.shortcuts import render
from django.http import HttpResponse
from .models import Consumed_Stats
from datetime import datetime

# Create your views here.
def statsHandler(request):
    stats_list = Consumed_Stats.objects.all()
    # Check if we want to show the stats table
    if stats_list:
        context = {'stats_list': stats_list}
        return render(request, 'stats/index.html', context)
    else :
        stats_list = False
        context = None
        return render(request, 'stats/index.html', context)

# Re-initializes the stats table with a parameter to distinguish the number
# of days to change
def reinitStats(day_diff):
    temp_count_array = [] # holds the values to be pushed to next day
    temp_count_array2 = [] # holds for an additonal day
    stats_list = Consumed_Stats.objects.all()

    # Since this function is only called when a new day is detected, by default
    # all count1 values will be zeroed.
    for i in range(0, len(stats_list)):
        temp_count_array.append(stats_list[i].count1)
        stats_list[i].count1 = 0
        stats_list[i].save()

    # Now iterate through the second day values, if the difference in days is
    # greater than 1 (though it checks equality), keep shifting over,
    # otherwise, set those values to zero
    for i in range(0, len(stats_list)):
        if (day_diff == 1):
            temp_count_array2.append(stats_list[i].count2)
            stats_list[i].count2 = temp_count_array[i]
            stats_list[i].save()
        else:
            temp_count_array[i] = stats_list[i].count2
            stats_list[i].count2 = 0
            stats_list[i].save()

    for i in range(0, len(stats_list)):
        if day_diff == 2:
            temp_count_array[i] = stats_list[i].count3
            stats_list[i].count3 = temp_count_array2[i]
            stats_list.save()
        else:
            temp_count_array[i] = stats_list[i].count3
            stats_list[i].count3 = 0
            stats_list.save()

    for i in range(0, len(stats_list)):
        if day_diff > 4:
            stats_list[i].count4 = 0
            stats_list.save()
        else:
            stats_list[i] = temp_count_array[i]
            stats_list.save()

    # Now cleanup
    cleanup()

# Cleanup fucntion remove food items in the stats table that have all counts
# equal to 0
def cleanup():
    stats_list = Consumed_Stats.objects.all()

    for i in range(0, len(stats_list)):
        if (stats_list[i].count1 == 0 and stats_list[i].count2 == 0 and
                stats_list[i].count3 == 0 and stats_list[i].count4 == 0):
                stats_list.remove()
