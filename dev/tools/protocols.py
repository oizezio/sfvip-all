from typing import Optional, Protocol, Sequence, runtime_checkable


class CfgFile(Protocol):
    path: str


@runtime_checkable
class CfgFileResize(CfgFile, Protocol):
    src: str
    resize: Optional[tuple[int, int]]


class CfgBuild(Protocol):
    ico: str
    main: str
    name: str
    company: str
    version: str
    dir: str
    update: str
    install_finish_page: bool

    @property
    def install_cmd(self) -> Sequence[str]:
        ...

    @property
    def uninstall_cmd(self) -> Sequence[str]:
        ...

    @property
    def files(self) -> Sequence[CfgFile | CfgFileResize]:
        ...

    @property
    def nuitka_args(self) -> Sequence[str]:
        ...


class CfgGithub(Protocol):
    owner: str
    repo: str


class CfgTemplate(Protocol):
    src: str
    dst: str


class CfgTemplates(Protocol):
    @property
    def all(self) -> Sequence[CfgTemplate]:
        ...


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


class CfgTexts(Protocol):
    language: str

    @staticmethod
    def as_dict() -> dict[str, str]:
        ...
