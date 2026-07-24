During this project I primarily used GitHub Copilot to assist with planning, implementation ideas, test generation, and documentation. AI was particularly useful when designing the search endpoint because it suggested a clean approach that reused the existing GET /tasks endpoint rather than introducing unnecessary APIs.

One area where AI slowed me down was implementing the comments feature. The generated task card modal was not responsive and did not support scrolling, which caused the footer and action buttons to be hidden.

The most valuable part of using AI was reviewing its suggestions instead of accepting them directly. For example, AI initially recommended searching task IDs in addition to titles and descriptions. After comparing this against the project requirements, I removed that behavior because only title and description searches were required.

Throughout the implementation I treated AI as an assistant rather than an authority. Every code suggestion was reviewed, tested, and adjusted before being incorporated. This process helped ensure that the final implementation remained consistent with the project's architecture while satisfying the assignment requirements. 