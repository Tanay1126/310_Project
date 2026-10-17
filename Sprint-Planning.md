# Sprint Planning XXX

## Sprint Information

- **Sprint / Milestone:** Milestone 1
- **Sprint dates:** 2026-10-05 to 2026-10-16
- **Planning meeting date:** 2026-10-05
- **Facilitator:** Yug Gullapalli

### Team Members

- [ ] Flower Meadows
- [ ] Gabriel Dantes
- [ ] Tanay Desai
- [ ] Yug Gullapalli

---

## 1. Sprint Goal

> What should the team have working by the end of this sprint?

**Sprint Goal:**

The team will have the first milestone slice finished by the end. That more specifically being the aspect of being able to manage a restaurant and be able to see through the eyes of a client.

---

## 2. Sprint Backlog

Select the user stories that the team commits to working on during this sprint.

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|------|-----------|---|
| #1 |A1| High  | We want users to see the contents in a list  |  Tanay |
| #2 |A2| Medium|We want users to see details  |  |   
| #3 |A | High  |Browsing restaurants  | |
| #4 |B | Medium|Add and update restaurant listing so that visitors can discover it | |

> **Important:** Primary ownership means that the student is responsible for coordinating the work. It does not mean that the student works alone or that other team members cannot contribute.

---

## 3. Task Decomposition

Break larger user stories into smaller tasks that can be implemented, reviewed, and tested.

### User Story #[NUMBER] — [TITLE]

- [x] User Story #1 - Expand Schemas beyond just Restaurants
- [x] User Story #1 - Update Routes/Services/Repositories to match
- [x] User Story #1 - Update data to match
- [x] User Story #1 - Create Front-End for viewing
- [x] Documentation / API updates

---

## 4. Dependencies and Integration

Identify work that depends on another team member, subsystem, or component.

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---------------------------|----------|------|-----|
| As a visitor, See a List of Restaurants | Story A1 |Tanay| Adapting a front end component that shows the list of restaurants|
|As a visitor, I want to view a restaurants detail and menu | Story A2 | Gabriel | Making schemas that display details for menu that customers can see  |
|As a directory maintainer, I want to add a restaurant | Story B1 | | |

### Integration Plan

<!-- Describe how the team will integrate the work during the sprint. -->

---

## 5. Risks and Potential Blockers

Identify anything that could prevent the team from achieving the sprint goal.

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| Dependency Preloading issue|Sometimes Unit Tests used to struggle with dependencies | It's been solved with modifying some of the backend code and yml errors | Meadow
| | | | |

---

## 6. Definition of Done

For work to be considered **DONE**, the team agrees that it must satisfy the following:

- [x] Requirements/acceptance criteria are satisfied.
- [x] Business logic is implemented in the appropriate service layer.
- [x] Persistence is handled through the repository layer.
- [x] Appropriate unit tests are included.
- [x] Appropriate integration/API tests are included.
- [x] Tests pass.
- [x] Code has been reviewed by at least one teammate.
- [x] Review feedback has been addressed.
- [x] Documentation has been updated where necessary.
- [x] The change is integrated into the team's working version.
- [x] No known critical defects remain.

---

## 7. Sprint Commitment

Before ending the meeting, each team member should confirm their understanding of the sprint plan.

| Team Member | Initial Responsibilities | Confirmed |
|---|---|---|
|Flower Meadows |tests and end checks | x |
|Gabriel Dantes |schemas and foundation | x |
|Tanay Desai |front-end and initial checks | x |
|Yug Gullapalli |documentation and overview | x |

---

## Meeting Notes

<!-- Add any additional notes, decisions, or questions from the planning meeting. -->
