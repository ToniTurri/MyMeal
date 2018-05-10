from django.shortcuts import render
from .models import Consumed_Stats, Time_Stamp
from django.utils import timezone
from datetime import timedelta
from inventory.models import InventoryItem


# Create your views here.
def statsHandler(request):
    # Check if we want to show the stats table
    inventory_items = InventoryItem.objects.filter(user=request.user)
    stats_list = Consumed_Stats.objects.filter(food__in=inventory_items).order_by('food__name')

    if stats_list:
        if timeCheck(request):
            # Need to re-get the list
            stats_list = Consumed_Stats.objects.filter(user=request.user).order_by('food__name')
        context = {'stats_list': stats_list,
                   'value': timezone.now(),
                   'value2': timezone.now() - timedelta(days=1),
                   'value3': timezone.now() - timedelta(days=2),
                   'value4': timezone.now() - timedelta(days=3)}
        return render(request, 'stats/index.html', context)

    stats_list = False
    context = None
    return render(request, 'stats/index.html', context)


# Re-initializes the stats table with a parameter to distinguish the number
# of days to change
def reinitStats(request, day_diff):
    temp_count_array = []  # holds the values to be pushed to next day
    temp_count_array2 = []  # hold additional day
    inventory_items = InventoryItem.objects.filter(user=request.user)
    stats_list = Consumed_Stats.objects.filter(food__in=inventory_items)

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
    cleanup(request)


# Cleanup fucntion remove food items in the stats table that have all counts
# equal to 0
def cleanup(request):
    inventory_items = InventoryItem.objects.filter(user=request.user)
    stats_list = Consumed_Stats.objects.filter(food__in=inventory_items)

    # Omit count1 since it's only called on new day and that day is 0
    for i in range(0, len(stats_list)):
        if (stats_list[i].count2 == 0 and stats_list[i].count3 == 0
                and stats_list[i].count4 == 0):
            stats_list[i].delete()


# Checks if the last day a food item was consumed or stat page accessed is
# different than the current day to reinitStats
def timeCheck(request):
    date = timezone.now() - timedelta(hours=4)

    stat_time = Time_Stamp.objects.filter(user=request.user).first()

    if not stat_time:
        stat_time = Time_Stamp(user=request.user, time=(timezone.now() - timedelta(hours=4)))
        stat_time.save()
    else:
        # find difference in days
        day_diff = abs(((date - timedelta(hours=date.hour, minutes=date.minute, seconds=date.second,
                                          microseconds=date.microsecond))
                        - (stat_time.time - timedelta(hours=stat_time.time.hour, minutes=stat_time.time.minute,
                                                      seconds=stat_time.time.second,
                                                      microseconds=stat_time.time.microsecond))).days)

        if day_diff is 0:
            return
        else:
            stat_time.time = timezone.now() - timedelta(hours=4)
            stat_time.save()
            if day_diff != 0:
                reinitStats(request, day_diff)
            return True
