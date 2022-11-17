import streamlit as st
import altair as alt
import pandas as pd

INCOME_ORDER = [
    '<$25,000',
    '$25,000 - $34,999',
    '$35,000 - $49,999',
    '$50,000 - $74,999',
    '$75,000 - $99,999',
    '$100,000 - $149,999',
    '$150,000 - $199,999',
    '>$200,000'
]

GENDER_ORDER = ["Female", "Male"]

AGE_GROUP_ORDER = [
    '18-24',
    '25-44',
    '45-64',
    '65+'
]

MARITAL_STATUS_ORDER = [
    'Married',
    'Widowed',
    'Divorced',
    'Separated',
    'Never married'
]

ORDERS = {
    "income": INCOME_ORDER,
    "gender": GENDER_ORDER,
    "age_group": AGE_GROUP_ORDER,
    "marital_status": MARITAL_STATUS_ORDER
}

ENCODINGS = {
    "income": "O",
    "gender": "N",
    "age_group": "O",
    "marital_status": "N",
    "race": "N"
}

@st.cache
def load_data():
    return pd.read_csv("pulse_survey_sampled.csv")

@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')
 
def get_slice_membership(df, genders=None, educations=None, races=None, age_range=None, marital_status=None, income=None):
    labels = pd.Series([1] * len(df), index=df.index)
    if genders:
        labels &= df['gender'].isin(genders)
    if educations:
        labels &= df['education'].isin(educations)
    if races:
        labels &= df['race'].isin(races)
    if age_range is not None:
        labels &= df['age'] >= age_range[0]
        labels &= df['age'] <= age_range[1]
    if marital_status:
        labels &= df['marital_status'].isin(marital_status)
    if income:
        labels &= df['income'].isin(income)
    return labels

@st.cache
def make_long_reason_dataframe(df, reason_prefix, field_name='reason', add_fields=[]):
    reasons = df[[c for c in df.columns if c.startswith(reason_prefix)] + add_fields + ['week']].copy()
    reasons['id'] = reasons.index
    reasons = pd.wide_to_long(reasons, reason_prefix, i='id', j=field_name, suffix='.+')
    reasons[reason_prefix] = reasons[reason_prefix].fillna(False)
    reasons = reasons.reset_index().rename({reason_prefix: '% agree'}, axis=1)
    grouped = reasons.groupby(['week', field_name] + add_fields).agg({'% agree': 'mean'}).reset_index()
    grouped['% agree'] = grouped['% agree'] * 100
    return grouped

df = load_data()

st.title("Are Economic Impact Payments effective?")

st.write("""
The Economic Impact Payments (EIP), also known as the stimulus checks, are
direct relief payments paid directly to
Americans during the COVID-19 crisis. In this Ethics Workshop, you will
select and/or develop visualizations to construct an argument about **whether or
not the EIPs have been effective at supporting Americans, and if similar
strategies should be used in future public emergencies.**

### Background

The Treasury Department, the Bureau of the Fiscal Service, and the Internal 
Revenue Service (IRS) sent out three rounds of EIPs, described below:

Starting in March 2020, the Coronavirus Aid, Relief, and Economic Security
Act (CARES Act) provided EIPs of up to \\$1,200 per adult for eligible
individuals and \\$500 per qualifying child under age 17.
The payments were reduced for individuals with adjusted gross income (AGI) greater
than \\$75,000 (\\$150,000 for married couples filing a joint return).  For a family
of four, these Economic Impact Payments provided up to \\$3,400 of direct 
financial relief.

The COVID-related Tax Relief Act of 2020, enacted in late December 2020,
authorized additional payments of up to \\$600 per adult for eligible individuals
and up to \\$600 for each qualifying child under age 17.  The AGI thresholds at
which the payments began to be reduced were identical to those under the CARES
Act.

The American Rescue Plan Act of 2021 (American Rescue Plan), enacted in early 
March 2021, provided Economic Impact Payments of up to \\$1,400 for eligible 
individuals or \\$2,800 for married couples filing jointly, plus \\$1,400 for 
each qualifying dependent, including adult dependents.

### Dataset

In this workshop, you will study the effect of EIPs using an extended version of the Household Pulse
Survey dataset. The dataset now includes survey responses from four two-week time periods:

* Week 20: November 25 - December 7 2020 *(8 months after the first EIP, just before the second EIP)*
* Week 25: February 17 - March 1 *(two months after the second EIP, just before the third EIP)*
* Week 27: March 17 - March 29 *(two months after the second EIP, during the third EIP rollout)*
* Week 28: April 14 - April 26 *(one month after the third EIP)*

Unfortunately, data on who had received the first round of EIPs is unavailable in Week 20.
Data can be found here: https://drive.google.com/file/d/1ij3QNFYQtKw7a_ZO1w5vrmg3uG0EQeE6/view?usp=sharing

### Instructions

You will choose to be either "pro"-stimulus or "anti"-stimulus.
Your task is to create a persuasive, narrative slide deck in Google Slides that uses
visualizations inspired by the ones on this page to argue your point of view.

1. Individually **explore the dataset** below and begin to identify some visualizations
   that could be used to help make your assigned case.
2. As a group in class or individually if you are doing this asychronously, **pitch and decide on 3 or more visualizations** that you want to create.
   Try to make your visualizations unique! Consider the following areas:

    * How did the EIPs affect Americans' spending and saving behavior?
    * How did EIPs affect Americans' emotional and mental health?
    * How did EIPs affect different subgroups of the population differently?

3. **Create the visualizations.** You can screenshot the charts from this page and
   apply additional annotations or modifications, or you can download the data
   used to generate each chart and create your own version in a charting tool of
   your choice. Add a few sentences about how the visualization supports your side.
4. **Compile the visualizations** you've created into a Google slide deck. Make
   sure each visualization has a persuasive title and caption.
5. Verify the slide deck is sharable among Andrew CMU users. You should **submit the link to the Google Slides presentation**
   on [this form](https://forms.gle/xaVkL5wmej75YHgQA).

""")

st.header("Slice Data")

st.write("""
You may optionally choose to curate a subset of the data to construct
your data narrative. The visualizations below will all use the slice you
define here.
""")

with st.expander("Demographic slicing"):
    cols = st.columns(3)
    with cols[0]:
        genders = st.multiselect('Gender', df['gender'].unique())
        educations = st.multiselect('Education', df['education'].unique())
    with cols[1]:
        marital_status = st.multiselect('Marital Status', df['marital_status'].unique())
        income = st.multiselect('Income', INCOME_ORDER)
    with cols[2]:
        races = st.multiselect('Race', df['race'].unique())
    age_range = st.slider('Age', min_value=int(df['age'].min()), max_value=int(df['age'].max()), value=(int(df['age'].min()), int(df['age'].max())))

    slice_labels = get_slice_membership(df, genders, educations, races, age_range, marital_status, income)
    slice_labels.name = "slice_membership"

with st.expander("Choose weeks"):
    st.write("""
The weeks you choose to display can have a big impact on the
trends you see. In particular, notice that Receipt of EIP question asks whether 
respondents received a check *in the last seven days*. How might the weeks in 
which you collect that data influence that trend?""")
    weeks_to_show = st.multiselect("Weeks to show", df['week'].unique())

    if weeks_to_show:
        slice_labels &= df['week'].isin([int(w) for w in weeks_to_show])

if slice_labels.sum() < len(df):
    st.info("{}/{} ({:.1f}%) individuals match the selected conditions.".format(slice_labels.sum(), len(df), slice_labels.sum() / len(df) * 100))

df = df[slice_labels]


st.header("Create Visualizations")
st.write("""
Browse the following sections to find data features and trends that you can use
to construct your argument. Note that which data features and subsets you show
or hide can have a significant effect on the story each visualization tells, so
choose carefully.

To show/hide charts, click into the expander and check the box labeled "Show chart".
""")

with st.expander("Spending sources"):
    st.write("""
This data shows the various sources from which survey respondents' spending money 
came from. Participants could select multiple responses. *Hint:* Try selecting an 
additional breakdown to highlight differences in spending sources between different 
demographic groups.""")
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show spending sources chart")
        include_cols = st.multiselect("Sources to show", [c.replace('spend_source_', '') for c in df.columns if 'spend_source_' in c])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='spending_source_breakdown_checkbox')
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "race", "age_group", "marital_status", "hhld_num_persons", "received_EIP"],
                                index=0,
                                key='spending_source_breakdown_select')
    
    if show_chart:
        plot_df = make_long_reason_dataframe(df,
                                             'spend_source_',
                                             field_name='Source',
                                             add_fields=[layering] if layering != 'none' else [])
        if include_cols:
            plot_df = plot_df[plot_df['Source'].isin(include_cols)]
        chart = alt.Chart(plot_df).mark_bar().encode(
            y=alt.Y('Source:O', sort='-x'),
            x=alt.X('% agree', stack=None),
            tooltip=['Source', '% agree']
        ).properties(width=200)
        if breakdown:
            chart = chart.encode(column='week:N', color='week:N')
        if layering != 'none':
            chart = chart.encode(row=f'{layering}:O', tooltip=['Source', '% agree', layering])
    
if chart:
    st.altair_chart(chart)
    st.download_button("Download Data",
                       data=convert_df(plot_df),
                       file_name='spending_source_data.csv',
                       mime='text/csv')



with st.expander("Reasons for changing spending habits"):
    st.write("""
This data provides answers as to why people might have changed their spending
habits in recent weeks. Notice that the reasons are paired, for example "Concerns
about the economy" is paired with "No longer concerned about the economy."
*Hint:* showing a smaller subset of reasons may result in a chart that tells a
more compelling story.""")
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show spending habits chart")
        include_cols = st.multiselect("Reasons to show", [c.replace('spending_change_', '') for c in df.columns if 'spending_change_' in c])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='spending_change_breakdown_checkbox')
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "race", "age_group", "marital_status", "hhld_num_persons", "received_EIP"],
                                index=0,
                                key='spending_change_breakdown_select')
    
    if show_chart:
        plot_df = make_long_reason_dataframe(df,
                                             'spending_change_',
                                             field_name='Reason',
                                             add_fields=[layering] if layering != 'none' else [])
        if include_cols:
            plot_df = plot_df[plot_df['Reason'].isin(include_cols)]
        chart = alt.Chart(plot_df).mark_bar().encode(
            y=alt.Y('Reason:O', sort='-x'),
            x=alt.X('% agree', stack=None),
            tooltip=['Reason', '% agree']
        ).properties(width=200)
        if breakdown:
            chart = chart.encode(column='week:N', color='week:N')
        if layering != 'none':
            chart = chart.encode(row=f'{layering}:O', tooltip=['Reason', '% agree', layering])
    
if chart:
    st.altair_chart(chart)
    st.download_button("Download Data",
                       data=convert_df(plot_df),
                       file_name='spending_habit_reasons.csv',
                       mime='text/csv')


with st.expander("Food spending habits"):
    st.write("""
This data indicates how many dollars respondents spent on unprepared food (such 
as groceries) as well as prepared food (e.g. restaurants). Checking the standard
error checkbox will show error bands that are larger when there is a smaller
sample size for the particular group. Showing these error bands may help to cast
skepticism on the trends.""")
    cols = st.columns(3)
    with cols[0]:
        show_unprepared = st.checkbox("Spending on Unprepared Food")
    with cols[1]:
        show_prepared = st.checkbox("Spending on Prepared Food")
    with cols[2]:
        show_ci = st.checkbox("Show Standard Error")
    breakdown = st.selectbox("Breakdown by", ["none", "income", "gender", "race", "age_group", "marital_status", "hhld_num_persons", "received_EIP"], index=0)

chart = None
if show_unprepared:
    plot_df = df.loc[~pd.isna(df[breakdown]), ['food_spending_unprepared', breakdown, 'week']] if breakdown != 'none' else df[['food_spending_unprepared', 'week']]
    chart = alt.Chart(plot_df).mark_line().encode(
        x='week:O',
        y='mean(food_spending_unprepared)'
    ).properties(width=300)
    if breakdown != 'none':
        chart = chart.encode(color=alt.Color(f"{breakdown}:{ENCODINGS.get(breakdown, 'O')}", sort=ORDERS.get(breakdown, 'ascending')))
    if show_ci:
        ci_chart = alt.Chart(plot_df).mark_errorband(extent='stderr').encode(
            x='week:O',
            y='food_spending_unprepared'
        )
        if breakdown != 'none':
            ci_chart = ci_chart.encode(color=alt.Color(f"{breakdown}:{ENCODINGS.get(breakdown, 'O')}", sort=ORDERS.get(breakdown, 'ascending')))
        chart = chart + ci_chart
    st.download_button("Download Unprepared Food Data",
                       data=convert_df(plot_df),
                       file_name='unprepared_food_data.csv',
                       mime='text/csv')

        
if show_prepared:
    plot_df = df.loc[~pd.isna(df[breakdown]), ['food_spending_prepared', breakdown, 'week']] if breakdown != 'none' else df[['food_spending_prepared', 'week']]
    new_chart = alt.Chart(plot_df).mark_line().encode(
        x='week:O',
        y='mean(food_spending_prepared)'
    ).properties(width=300)
    if breakdown != 'none':
        new_chart = new_chart.encode(color=alt.Color(f"{breakdown}:{ENCODINGS.get(breakdown, 'O')}", sort=ORDERS.get(breakdown, 'ascending')))
    if show_ci:
        ci_chart = alt.Chart(plot_df).mark_errorband(extent='stderr').encode(
            x='week:O',
            y='food_spending_prepared'
        )
        if breakdown != 'none':
            ci_chart = ci_chart.encode(color=alt.Color(f"{breakdown}:{ENCODINGS.get(breakdown, 'O')}", sort=ORDERS.get(breakdown, 'ascending')))
        new_chart = new_chart + ci_chart
    if chart is not None: chart = chart | new_chart
    else: chart = new_chart
    st.download_button("Download Prepared Food Data",
                       data=convert_df(plot_df),
                       file_name='prepared_food_data.csv',
                       mime='text/csv')


if chart:
    st.altair_chart(chart)        
# st.altair_chart( | alt.Chart(df.loc[~pd.isna(df['income']), ['food_spending_prepared', 'income', 'week']]).mark_line().encode(
#     x='week:O',
#     y='mean(food_spending_prepared)',
#     color=alt.Color('income:O', sort=ORDERS.get(breakdown, 'ascending')),
# ).properties(width=300), use_container_width=True)



with st.expander("Receipt of EIP"):
    st.write("""
This data is a simple indication of how many people have received a stimulus
check **within the last 7 days** of each time point. *Hint:* The data might tell
a different story depending on whether you choose to plot as percentages or as
raw counts.""")
    chart = None
    cols = st.columns(2)
    field = 'received_EIP'
    with cols[0]:
        show_chart = st.checkbox("Show receipt of EIP chart")
        percentage = st.checkbox("Show as percentage", value=True)
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='eip_receipt_breakdown_checkbox')
    cols = st.columns(2)
    with cols[0]:
        values_to_show = st.selectbox("Values to show", ["Both", "Received EIP", "Did not receive EIP"])
    with cols[1]:
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "race", "age_group", "marital_status", "hhld_num_persons"],
                                index=0,
                                key='eip_receipt_breakdown_select')
            
    if show_chart:
        data_to_show = df[~pd.isna(df[field])]
        single_value = values_to_show != 'Both'
        if values_to_show.startswith("Did not"):
            data_to_show = df.copy()
            field = "did_not_receive_EIP"
            data_to_show[field] = ~(data_to_show["received_EIP"].astype(bool))
        
        count_field = 'val_count' if not percentage else 'val_fraction'
        data_to_show = (data_to_show
                        .groupby(['week'] + ([layering] if layering != 'none' else []))[field]
                        .value_counts(normalize=percentage)
                        .reset_index(name=count_field))
        if single_value:
            data_to_show = data_to_show[data_to_show[field]]
        
        chart = alt.Chart(data_to_show).mark_bar()
        if percentage:
            chart = chart.transform_calculate(
                val_percentage=f"100 * datum.{count_field}",
            )
            count_field = 'val_percentage'
        count_field = count_field + ':Q'
        if breakdown:
            chart = chart.encode(
                y=field,
                x=count_field,
                tooltip=['week', field, count_field]
            )
            if single_value:
                chart = chart.encode(row='week:N')
            else:
                chart = chart.encode(column='week:N')
        else:
            chart = chart.encode(
                y=field,
                x=count_field,
                tooltip=[field, count_field]
            )
        if layering != 'none':
            if single_value:
                chart = chart.encode(y=alt.Y(f"{layering}:{ENCODINGS.get(layering, 'O')}", sort=ORDERS.get(layering, 'ascending')),
                                     color='week:N',
                                     tooltip=[layering, field, count_field] + (['week'] if breakdown else []))
            else:
                chart = chart.encode(row=alt.Color(f"{layering}:{ENCODINGS.get(layering, 'O')}", sort=ORDERS.get(layering, 'ascending')),
                                     color='week:N',
                                    tooltip=[layering, field, count_field] + (['week'] if breakdown else []))
        elif breakdown:
            chart = chart.encode(color='week:N')


if chart is not None:
    st.altair_chart(chart)
    st.download_button("Download Data",
                       data=convert_df(data_to_show),
                       file_name='eip_receipt_data.csv',
                       mime='text/csv')



with st.expander("EIP spending targets"):
    st.write("""
These data shed light on how people are spending money from stimulus checks.
Respondents could select multiple choices. *Hint:* Try selecting just a few
spending targets to tell a more focused story with your chart.""")
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show EIP spending targets chart")
        include_cols = st.multiselect("Targets to show", [c.replace('eip_spend_', '') for c in df.columns if 'eip_spend_' in c])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='spending_target_breakdown_checkbox')
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "race", "age_group", "marital_status", "hhld_num_persons"],
                                index=0,
                                key='spending_target_breakdown_select')
    
    if show_chart:
        plot_df = make_long_reason_dataframe(df[df['week'] != 20],
                                             'eip_spend_',
                                             field_name='Target',
                                             add_fields=[layering] if layering != 'none' else [])
        if include_cols:
            plot_df = plot_df[plot_df['Target'].isin(include_cols)]
        chart = alt.Chart(plot_df).mark_bar().encode(
            y=alt.Y('Target:O', sort='-x'),
            x=alt.X('% agree', stack=None),
            tooltip=['Target', '% agree']
        ).properties(width=250)
        if breakdown:
            chart = chart.encode(column='week:N', color='week:N')
        if layering != 'none':
            chart = chart.encode(row=f'{layering}:O', tooltip=['Target', '% agree', layering])
    
        
if show_chart:
    st.altair_chart(chart)
    st.download_button("Download Data",
                       data=convert_df(plot_df),
                       file_name='spending_targets_data.csv',
                       mime='text/csv')



with st.expander("Mental health data"):
    st.write("""
The dataset includes four features indicating people's mental health status during
each time period: anxiety, frequent worry, feeling down and depressed, and having
little interest in doing things. For each feature, respondents rated their
feelings from 1-4, where 1 indicates very infrequent and 4 indicates very frequent.
If you show the data as a line chart, the values plotted are the average ratings
ranging from 1 to 4.""")
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show mental health chart")
        chart_type = st.selectbox("Chart type", ["Line", "Bar"])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='mh_breakdown_checkbox', disabled=chart_type == "Line")
    cols = st.columns(2)
    with cols[0]:
        field = st.selectbox("Indicator", ["anxious_freq", "worry_freq", "depressed_freq", "little_interest_freq"])
    with cols[1]:
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "race", "age_group", "marital_status", "hhld_num_persons", "received_EIP"],
                                index=0,
                                key='mh_breakdown_select')
    
    if show_chart:
        if chart_type == "Line":
            data_to_show = df[~pd.isna(df[field])]

            data_to_show = data_to_show.groupby(['week'] + ([layering] if layering != 'none' else [])).agg({field: 'mean'}).reset_index()
            
            chart = alt.Chart(data_to_show).mark_line()
            # chart = alt.Chart(df.loc[~pd.isna(df[field]), [field, 'week'] + ([layering] if layering != 'none' else [])]).mark_bar()
            chart = chart.encode(
                x='week:N',
                y=alt.Y(field, scale=alt.Scale(domain=(1, 4))),
                tooltip=['week', field]
            ).properties(width=400)
            if layering != 'none':
                chart = chart.encode(color=alt.Color(f"{layering}:{ENCODINGS.get(layering, 'O')}", sort=ORDERS.get(layering, 'ascending')),
                                     tooltip=[layering, field] + (['week'] if breakdown else [])) 
                            
        elif chart_type == "Bar":
            data_to_show = df[~pd.isna(df[field])]

            count_field = 'val_count' if not percentage else 'val_fraction'
            data_to_show = (data_to_show
                            .groupby(['week'] + ([layering] if layering != 'none' else []))[field]
                            .value_counts(normalize=percentage)
                            .reset_index(name=count_field))
            
            chart = alt.Chart(data_to_show).mark_bar()
            # chart = alt.Chart(df.loc[~pd.isna(df[field]), [field, 'week'] + ([layering] if layering != 'none' else [])]).mark_bar()
            if breakdown:
                chart = chart.encode(
                    x='week:N',
                    y=count_field,
                    column=f'{field}:O',
                    tooltip=['week', count_field, field]
                )
            else:
                chart = chart.encode(
                    x=f'{field}:O',
                    y=count_field,
                    tooltip=[field, count_field]
                )
            if layering != 'none':
                chart = chart.encode(row=alt.Row(f"{layering}:{ENCODINGS.get(layering, 'O')}", sort=ORDERS.get(layering, 'ascending')),
                                        color='week:N',
                                    tooltip=[layering, field, count_field] + (['week'] if breakdown else []))
                chart = chart.properties(height=150)
            elif breakdown:
                chart = chart.encode(color='week:N')

if chart is not None:
    st.altair_chart(chart)
    st.download_button("Download Data",
                       data=convert_df(data_to_show),
                       file_name='mental_health_data.csv',
                       mime='text/csv')



st.header("Additional Tools")

st.write("See below for summary information about the demographics in the dataset, or to view a random sample of the data.")

with st.expander("Dataset Demographics"):
    cols = st.columns(2)
    with cols[0]:
        st.altair_chart(alt.Chart(df['gender'].value_counts().reset_index(), title='Gender').mark_arc().encode(
            theta='gender',
            color='index:N',
            tooltip=['gender', 'index']
        ).configure_view(
            strokeWidth=0
        ), use_container_width=True)
    with cols[1]:
        st.altair_chart(alt.Chart(df['marital_status'].value_counts().reset_index(), title='Marital Status').mark_arc().encode(
            theta='marital_status',
            color='index:N',
            tooltip=['marital_status', 'index']
        ).configure_view(
            strokeWidth=0
        ), use_container_width=True)
        
    cols = st.columns(2)
    with cols[0]:
        st.altair_chart(alt.Chart(df['race'].value_counts().reset_index(), title='Race').mark_arc().encode(
            theta='race',
            color='index:N',
            tooltip=['race', 'index']
        ).configure_view(
            strokeWidth=0
        ), use_container_width=True)
    with cols[1]:
        st.altair_chart(alt.Chart(df['hispanic'].value_counts().reset_index(), title='Hispanic').mark_arc().encode(
            theta='hispanic',
            color='index:N',
            tooltip=['hispanic', 'index']
        ).configure_view(
            strokeWidth=0
        ), use_container_width=True)
            
    cols = st.columns(2)
    with cols[0]:
        st.altair_chart(alt.Chart(df['income'].value_counts().reset_index(), title='Income').mark_arc().encode(
            theta=alt.Theta('income', sort=INCOME_ORDER),
            color='index:N',
            tooltip=['income', 'index']
        ).configure_view(
            strokeWidth=0
        ), use_container_width=True)
    with cols[1]:
        st.altair_chart(alt.Chart(df['age'].reset_index(), title='Age').mark_bar().encode(
            x=alt.X('age', bin=alt.Bin(step=5)),
            y='count()',
            tooltip='count()'
        ).configure_view(
            strokeWidth=0
        ), use_container_width=True)
    
    st.altair_chart(alt.Chart(df['education'].value_counts().reset_index(), title='Education').mark_bar().encode(
        x='education',
        y=alt.X('index:N', sort=[
            'Less than high school',
            'Some high school',
            'High school graduate or equivalent',
            'Some college',
            'Associates degree',
            'Bachelors degree',
            'Graduate degree'
        ]),
        tooltip=['education', 'index']
    ).configure_view(
        strokeWidth=0
    ), use_container_width=True)
        
if st.checkbox("Show sample of raw data"):
    st.dataframe(df.sample(n=20))