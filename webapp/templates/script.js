const result = document.querySelector(".list-group");

let list = [];

let keywords = [
  "Roma",
  "Napoli",
  "Milano",
  "Ancona",
  "Firenze"
];

const startsWith = (keyword, inputKeyword) =>
  keyword.toLocaleLowerCase().startsWith(inputKeyword.toLocaleLowerCase());

const includes = (keyword, inputKeyword) =>
  keyword.toLocaleLowerCase().includes(inputKeyword.toLocaleLowerCase());

const generateList = () => (list = list.map((data) => (data = liTag(data))));

const showList = (inputKeyword) => {
  result.classList.add("show");
  result.innerHTML = list.join("") || liTag(inputKeyword);
};

const hideList = () => {
  list = [];
  result.innerHTML = list;
  result.classList.remove("show");
};

const liTag = (value) =>
  `<li class="list-group-item">${value}</li>`;

const search = (e) => {
  let keyword = e.target.value;

  if (keyword) {
    filter(keyword);
    generateList();
    showList(keyword);
  } else hideList();
};

const filter = (inputKeyword) =>
  (list = keywords.filter(
    (keyword) =>
      startsWith(keyword, inputKeyword) || includes(keyword, inputKeyword)
  ));