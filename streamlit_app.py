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

@st.cache
def load_data():
    return pd.read_csv("pulse_survey_sampled.csv", dtype={
        "age": pd.Int64Dtype(), 
        "hhld_num_persons": pd.Int64Dtype(),
        "food_spending_unprepared": pd.Int64Dtype(), 
        "food_spending_prepared": pd.Int64Dtype()})

@st.cache
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
The Economic Impact Payments (EIP) are direct relief payments paid directly to
Americans during the COVID-19 crisis. In this Critique Workshop, you will
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

In this workshop, you will be using an extended version of the Household Pulse
Survey dataset, which you may recognize from the Interactivity Lab. The dataset
has been augmented to include survey responses from three two-week time periods:

* Week 20: November 25 - December 7
* Week 25: February 17 - March 1
* Week 28: April 14 - April 26

Note that Week 20 was conducted before the second round of EIPs, while Week 25
was conducted before the third round of EIPs. Unfortunately, data on who had
received the first round of EIPs is missing in Week 20.
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
    age_range = st.slider('Age', min_value=df['age'].min(), max_value=df['age'].max(), value=(df['age'].min(), df['age'].max()))

    slice_labels = get_slice_membership(df, genders, educations, races, age_range, marital_status, income)
    slice_labels.name = "slice_membership"

if slice_labels.sum() < len(df):
    st.info("{}/{} ({:.1f}%) individuals match the selected conditions.".format(slice_labels.sum(), len(df), slice_labels.sum() / len(df) * 100))

df = df[slice_labels]


st.header("Create Visualizations")
st.write("""
Browse the following sections to find data features and trends that you can use
to construct your argument. Note that which data features and subsets you show
or hide can have a significant effect on the story each visualization tells, so
choose carefully.
""")

with st.expander("Spending sources"):
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show spending sources chart")
        include_cols = st.multiselect("Sources to show", [c.replace('spend_source_', '') for c in df.columns if 'spend_source_' in c])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='spending_source_breakdown_checkbox')
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "age_group", "marital_status", "hhld_num_persons", "received_EIP"],
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



with st.expander("Reasons for changing spending habits"):
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show spending habits chart")
        include_cols = st.multiselect("Reasons to show", [c.replace('spending_change_', '') for c in df.columns if 'spending_change_' in c])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='spending_change_breakdown_checkbox')
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "age_group", "marital_status", "hhld_num_persons", "received_EIP"],
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


with st.expander("Food spending habits"):
    cols = st.columns(3)
    with cols[0]:
        show_unprepared = st.checkbox("Spending on Unprepared Food")
    with cols[1]:
        show_prepared = st.checkbox("Spending on Prepared Food")
    with cols[2]:
        show_ci = st.checkbox("Show Standard Error")
    breakdown = st.selectbox("Breakdown by", ["none", "income", "gender", "age_group", "marital_status", "hhld_num_persons", "received_EIP"], index=0)

chart = None
if show_unprepared:
    plot_df = df.loc[~pd.isna(df[breakdown]), ['food_spending_unprepared', breakdown, 'week']] if breakdown != 'none' else df[['food_spending_unprepared', 'week']]
    chart = alt.Chart(plot_df).mark_line().encode(
        x='week:O',
        y='mean(food_spending_unprepared)'
    ).properties(width=300)
    if breakdown != 'none':
        chart = chart.encode(color=alt.Color(f'{breakdown}:O', sort=ORDERS.get(breakdown, 'ascending')))
    if show_ci:
        ci_chart = alt.Chart(plot_df).mark_errorband(extent='stderr').encode(
            x='week:O',
            y='food_spending_unprepared'
        )
        if breakdown != 'none':
            ci_chart = ci_chart.encode(color=alt.Color(f'{breakdown}:O', sort=ORDERS.get(breakdown, 'ascending')))
        chart = chart + ci_chart
        
if show_prepared:
    plot_df = df.loc[~pd.isna(df[breakdown]), ['food_spending_prepared', breakdown, 'week']] if breakdown != 'none' else df[['food_spending_prepared', 'week']]
    new_chart = alt.Chart(plot_df).mark_line().encode(
        x='week:O',
        y='mean(food_spending_prepared)'
    ).properties(width=300)
    if breakdown != 'none':
        new_chart = new_chart.encode(color=alt.Color(f'{breakdown}:O', sort=ORDERS.get(breakdown, 'ascending')))
    if show_ci:
        ci_chart = alt.Chart(plot_df).mark_errorband(extent='stderr').encode(
            x='week:O',
            y='food_spending_prepared'
        )
        if breakdown != 'none':
            ci_chart = ci_chart.encode(color=alt.Color(f'{breakdown}:O', sort=ORDERS.get(breakdown, 'ascending')))
        new_chart = new_chart + ci_chart
    if chart is not None: chart = chart | new_chart
    else: chart = new_chart

if chart:
    st.altair_chart(chart)        
# st.altair_chart( | alt.Chart(df.loc[~pd.isna(df['income']), ['food_spending_prepared', 'income', 'week']]).mark_line().encode(
#     x='week:O',
#     y='mean(food_spending_prepared)',
#     color=alt.Color('income:O', sort=ORDERS.get(breakdown, 'ascending')),
# ).properties(width=300), use_container_width=True)



with st.expander("Receipt of EIP"):
    chart = None
    cols = st.columns(2)
    field = 'received_EIP'
    with cols[0]:
        show_chart = st.checkbox("Show receipt of EIP chart")
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='eip_receipt_breakdown_checkbox')
    layering = st.selectbox("Stacking",
                            ["none", "income", "gender", "age_group", "marital_status", "hhld_num_persons"],
                            index=0,
                            key='eip_receipt_breakdown_select')
    
    if show_chart:
        chart = alt.Chart().mark_bar().encode(
            y=field,
            x='count()',
            row='week:N'
        )
        chart = alt.Chart(df[[field, 'week'] + ([layering] if layering != 'none' else [])]).mark_bar()
        if breakdown:
            chart = chart.encode(
                y=field,
                x='count()',
                row='week:N',
                tooltip=['week', field, 'count()']
            )
        else:
            chart = chart.encode(
                y=field,
                x='count()',
                tooltip=[field, 'count()']
            )
        if layering != 'none':
            chart = chart.encode(color=alt.Color(f'{layering}:O', sort=ORDERS.get(layering, 'ascending')),
                                 tooltip=[layering, field, 'count()'] + (['week'] if breakdown else []))
        elif breakdown:
            chart = chart.encode(color='week:N')


if chart is not None:
    st.altair_chart(chart)



with st.expander("EIP spending targets"):
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show EIP spending targets chart")
        include_cols = st.multiselect("Targets to show", [c.replace('eip_spend_', '') for c in df.columns if 'eip_spend_' in c])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='spending_target_breakdown_checkbox')
        layering = st.selectbox("Additional breakdown",
                                ["none", "income", "gender", "age_group", "marital_status", "hhld_num_persons"],
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



with st.expander("Mental health data"):
    chart = None
    cols = st.columns(2)
    with cols[0]:
        show_chart = st.checkbox("Show mental health chart")
        field = st.selectbox("Indicator", ["anxious_freq", "worry_freq", "depressed_freq", "little_interest_freq"])
    with cols[1]:
        breakdown = st.checkbox("Breakdown by week", value=True, key='mh_breakdown_checkbox')
        layering = st.selectbox("Stacking",
                                ["none", "income", "gender", "age_group", "marital_status", "hhld_num_persons", "received_EIP"],
                                index=0,
                                key='mh_breakdown_select')
    
    if show_chart:
        chart = alt.Chart(df.loc[~pd.isna(df[field]), [field, 'week'] + ([layering] if layering != 'none' else [])]).mark_bar()
        if breakdown:
            chart = chart.encode(
                x='week:N',
                y='count()',
                column=f'{field}:O',
                tooltip=['week', 'count()', field]
            )
        else:
            chart = chart.encode(
                x=f'{field}:O',
                y='count()',
                tooltip=[field, 'count()']
            )
        if layering != 'none':
            chart = chart.encode(color=alt.Color(f'{layering}:O', sort=ORDERS.get(layering, 'ascending')),
                                 tooltip=[layering, field, 'count()'] + (['week'] if breakdown else []))
        elif breakdown:
            chart = chart.encode(color='week:N')

if chart is not None:
    st.altair_chart(chart)



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