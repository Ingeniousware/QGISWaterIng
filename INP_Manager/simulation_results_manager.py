"""public class RepositoryResponse
{
    /// <summary>
    /// 
    /// </summary>
    /// <param name="totalItems"></param>
    /// <param name="pageNumber"></param>
    /// <param name="pageSize"></param>
    public void Initialize(int totalItems, int pageNumber = 1, int pageSize = 10)
    {
        this.CurrentPage = pageNumber;
        this.TotalItems = totalItems;

        if (pageSize > 0)
        {
            this.PageSize = pageSize;

            this.TotalPages = (int)Math.Ceiling((decimal)totalItems / (decimal)pageSize);

            if (pageNumber > this.TotalPages)
                this.CurrentPage = this.TotalPages;

            this.StartPage = pageNumber - 5;
            this.EndPage = pageNumber + 4;

            if (this.StartPage <= 0)
            {
                this.EndPage -= (this.StartPage - 1);
                this.StartPage = 1;
            }

            if (this.EndPage > this.TotalPages)
            {
                this.EndPage = this.TotalPages;

                if (this.EndPage > 10)
                {
                    this.StartPage = this.EndPage - 9;
                }
            }

        }
        else
        {
            this.TotalPages = 1;
            this.CurrentPage = 1;
            this.StartPage = 1;
            this.EndPage = 1;
        }

        this.Meg = this.TotalPages == 0
            ? "No se encuentra ninguna elemento."
            : $"Mostrando página {this.CurrentPage} de {TotalPages}. Total: {totalItems} elementos";
    }

    public int TotalItems { get; set; }

    public int CurrentPage { get; set; }

    public int PageSize { get; set; }

    public int TotalPages { get; set; }

    public int StartPage { get; set; }

    public int EndPage { get; set; }

    public string Meg { get; set; } = string.Empty;

    public object? Items { get; set; }
}"""
class SimulationResultsManager:
    def __init__(self):
        self.total_items = 0
        self.current_page = 1
        self.page_size = 10
        self.total_pages = 1
        self.start_page = 1
        self.end_page = 1
        self.meg = ""
        self.items = None

    def initialize(self, total_items, page_number = 1, page_size = 10):
        self.current_page = page_number
        self.total_items = total_items

        if page_size > 0:
            self.page_size = page_size
            self.total_pages = (total_items + page_size - 1) // page_size  # equivalente a Math.Ceiling

            if page_number > self.total_pages:
                self.current_page = self.total_pages

            self.start_page = page_number - 5
            self.end_page = page_number + 4

            if self.start_page <= 0:
                self.end_page -= (self.start_page - 1)
                self.start_page = 1

            if self.end_page > self.total_pages:
                self.end_page = self.total_pages
                if self.end_page > 10:
                    self.start_page = self.end_page - 9
        else:
            self.total_pages = 1
            self.current_page = 1
            self.start_page = 1
            self.end_page = 1

        self.meg = (
            "No se encuentra ninguna elemento."
            if self.total_pages == 0
            else f"Mostrando página {self.current_page} de {self.total_pages}. Total: {total_items} elementos"
        )