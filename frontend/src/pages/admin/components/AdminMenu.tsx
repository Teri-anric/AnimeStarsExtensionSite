interface AdminMenuTab {
  id: string;
  label: string;
  path: string;
}

interface AdminMenuProps {
  tabs: AdminMenuTab[];
  activeTab: string;
  onNavigate: (path: string) => void;
}

const AdminMenu = ({ tabs, activeTab, onNavigate }: AdminMenuProps) => {
  return (
    <nav className="admin-nav" aria-label="Admin menu">
      {tabs.map((tab) => (
        <a
          key={tab.id}
          href={tab.path}
          className={`admin-nav-item ${activeTab === tab.id ? 'active' : ''}`}
          onClick={(e) => {
            e.preventDefault();
            onNavigate(tab.path);
          }}
        >
          <span>{tab.label}</span>
        </a>
      ))}
    </nav>
  );
};

export default AdminMenu;
