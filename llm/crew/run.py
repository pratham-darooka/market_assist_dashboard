import os
from crewai import Agent, Task, Crew
# Importing crewAI tools
from crewai_tools import (
    SerperDevTool,
    WebsiteSearchTool,
    YoutubeVideoSearchTool
)


# Assemble a crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    verbose=True
)

if __name__ == "__main__":
    # Execute tasks
    crew.kickoff()