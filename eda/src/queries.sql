select
    stops.reason_for_stop,
    (select min(rl.label) from reason_labels rl where rl.code = stops.reason_for_stop) as reason_label,
    count(*) as count
from stops
group by stops.reason_for_stop
order by count desc

select stops.data_year,
    sum(stops.sor_straight)
from stops
group by stops.data_year
order by stops.data_year

select count(distinct stops.loc_closest_city) as num_cities
from stops
