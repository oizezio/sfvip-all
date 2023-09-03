from typing import Protocol, Sequence, runtime_checkable


class CfgFile(Protocol):
    path: str


@runtime_checkable
class CfgFileResize(CfgFile, Protocol):
    src: str
    resize: tuple[int, int]


class CfgBuild(Protocol):
    ico: str
    main: str
    name: str
    company: str
    version: str
    dir: str

    @property
    def files(self) -> Sequence[CfgFile | CfgFileResize]:
        ...

    @property
    def nuitka_args(self) -> Sequence[str]:
        ...


class _CfgTemplate(Protocol):
    src: str
    dst: str


class CfgTemplates(Protocol):
    @property
    def all(self) -> Sequence[_CfgTemplate]:
        ...

    class Github(Protocol):
        owner: str
        repo: str


class _CfgEnvironment(Protocol):
    path: str

    @property
    def requirements(self) -> Sequence[str]:
        ...


class CfgEnvironments(Protocol):
    # pylint: disable=invalid-name
    @property
    def X86(self) -> _CfgEnvironment:
        ...

    @property
    def X64(self) -> _CfgEnvironment:
        ...
