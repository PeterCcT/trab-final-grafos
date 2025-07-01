from dataclasses import dataclass
from typing import Optional, TypedDict

@dataclass
class IssuesCursors(TypedDict):
    issuesCursor: Optional[str] = None
    commentsCursor: Optional[str] = None
    reactionsCursor: Optional[str] = None

@dataclass
class Reaction(TypedDict):
    content: str
    user: str

@dataclass
class Comment(TypedDict):
    author: str
    createdAt: str
    bodyText: str
    reactions: list[Reaction]

@dataclass
class Issue(TypedDict):
    number: int
    title: str
    author: str
    createdAt: str
    closedAt: Optional[str]