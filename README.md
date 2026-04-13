# Question -> Data -> Insight: Helping Students Make Better Career Decisions

## Part A: README Documentation

### 1) Explaining the Lifecycle

Data science does not begin with a dashboard or a model. It begins with a decision that needs to be made.

#### Question: define the decision before touching data

A strong project starts with a clear question, because the question defines:
- what problem matters,
- who will use the answer,
- and what action might change because of the answer.

If the question is vague (for example, "analyze labour market trends"), the work can become a collection of random charts with no direction.  
If the question is specific (for example, "Which skills are associated with faster job placement for entry-level data roles in our region?"), we can choose relevant data and avoid wasted effort.

This step is critical because every later step depends on it: what data we collect, how we evaluate quality, and what counts as a useful result.

#### Data: treat data as evidence, not just files

After defining the question, data becomes the evidence used to answer it.  
Understanding data means more than loading a CSV. It means asking:
- Where did this data come from?
- Who is represented and who is missing?
- What does each column actually measure?
- Over what time period is it valid?
- What biases or inconsistencies might affect conclusions?

In labour market analysis, this could include job postings, placement outcomes, salary ranges, regional demand, and course enrollment data.  
Before analysis, we need to check whether these sources are trustworthy, comparable, and aligned to the question.

If we skip this understanding step, we risk producing confident but wrong conclusions (for example, overvaluing a skill simply because one platform over-reports certain job titles).

#### Insight: create understanding that supports action

Insights are not "numbers on a chart."  
An insight is a meaningful finding that changes a decision.

Example:
- A number: "Python appears in 62% of postings."
- An insight: "Students with Python + SQL + one visualization tool have higher placement rates within six months than students with Python alone."

Insights emerge through exploration, comparison, and interpretation in context.  
Tools help compute patterns, but human reasoning turns patterns into decisions.

#### How the lifecycle connects

The lifecycle is sequential but also iterative:
1. The **question** gives focus.
2. **Data** provides evidence to test that question.
3. **Insight** explains what the evidence means for a real decision.
4. New insights often refine the original question, and the cycle repeats.

Without a clear question, data work becomes noisy.  
Without understanding data, insights are unreliable.  
Without insight, analysis has no decision value.

---

### 2) Applying the Lifecycle to a Project Context

#### Project context

A university career services team wants to improve graduate job placement in technology roles.

#### Question

Which skill combinations are most strongly associated with successful placement into entry-level tech jobs within six months of graduation?

This question is actionable because it can influence curriculum updates, workshop planning, and student advising.

#### Data needed

To answer this, I would combine:
- **Labour market data** from job boards/APIs: required skills, job titles, location, and posting frequency.
- **Graduate outcome data** from the university: student skills/certifications, internship experience, and placement status/timeline.
- **Program data** from internal systems: course completion and project/portfolio participation.

What this data represents:
- employer demand (external market signal),
- student preparation (skills built),
- and real outcomes (whether students were placed and how quickly).

Before analysis, I would standardize skill names (for example, "Power BI" vs "PowerBI"), align time windows, and remove duplicated postings.

#### Useful insight for decisions

A useful insight would be something like:
"Students who completed coursework in SQL, Python, and dashboarding, plus at least one internship, had the highest probability of placement within six months in this region."

This is useful because decision-makers can act on it:
- advisors can recommend clearer learning paths,
- students can prioritize high-impact skills earlier,
- and faculty can adjust electives to match demand.

The goal is not to predict perfectly; it is to make better educational and career decisions using evidence.

---

## Part B: Video Walkthrough Guide (~2 Minutes)

Use this README as your screen-share anchor and explain your reasoning in plain language.

### Suggested flow

1. **(0:00-0:30)** Introduce the lifecycle and why data science starts with a question.
2. **(0:30-1:10)** Explain Question -> Data -> Insight using your labour market example.
3. **(1:10-1:40)** Walk through your project context and what data you would use.
4. **(1:40-2:00)** Answer the mandatory scenario-based prompt.

### Scenario-based response (what to say)

If a dataset has many columns but no problem statement, I would pause modeling and align on a decision-focused question first.  
I would explain that jumping into visualizations or models immediately creates risk: we may optimize for patterns that are irrelevant, misread columns we do not understand, or produce outputs that no stakeholder can use.

Using the Question -> Data -> Insight framework, I would:
1. Define the decision and target user of the analysis.
2. Audit the dataset to understand what each field means, data quality limits, and representation gaps.
3. Explore only the data that directly supports the defined question.
4. Translate findings into an actionable insight, not just charts.

This realigns the work from "seeing what comes out" to producing evidence that supports a real decision.
